import os
import asyncio
import aiohttp
import time
import queue
import threading
import random
import logging

from typing import Dict, List, Any, Optional, Set

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from ruchky_backend.pets.models import Breed, Species

# Get API keys from environment variables
CATS_API_KEY = os.getenv("CATS_API_KEY", "")
DOGS_API_KEY = os.getenv("DOGS_API_KEY", "")

# Rate limiting parameters
MIN_REQUEST_INTERVAL = 0.2  # Minimum time between requests in seconds
MAX_REQUEST_INTERVAL = 0.5  # Maximum time between requests in seconds (adds jitter)


class Command(BaseCommand):
    help = "Seeds the database with dog and cat breeds with images from online APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing breeds before seeding",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Skip downloading breed images",
        )
        parser.add_argument(
            "--retry",
            type=int,
            default=3,
            help="Number of retries for image downloads (default: 3)",
        )
        parser.add_argument(
            "--concurrency",
            type=int,
            default=3,
            help="Maximum number of concurrent API requests (default: 3)",
        )
        parser.add_argument(
            "--rate-limit",
            type=float,
            default=0.3,
            help="Minimum seconds between API requests (default: 0.3)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output for debugging",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.skip_images = options.get("skip_images", False)
        self.retry_count = options.get("retry", 3)
        self.concurrency = options.get("concurrency", 3)
        self.rate_limit = options.get("rate-limit", 0.3)
        self.verbose = options.get("verbose", False)

        # Configure logging
        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger("breed_seeder")

        # Update rate limiting parameters based on options
        global MIN_REQUEST_INTERVAL, MAX_REQUEST_INTERVAL
        MIN_REQUEST_INTERVAL = self.rate_limit
        MAX_REQUEST_INTERVAL = self.rate_limit * 1.5

        # Create image processing queue and shared state
        self.image_queue = queue.Queue()
        self.processing_complete = threading.Event()
        self.successful_images = 0
        self.failed_images = 0

        # Create rate limiting locks for each API
        self.cat_api_lock = asyncio.Lock()
        self.dog_api_lock = asyncio.Lock()
        self.last_cat_request_time = 0
        self.last_dog_request_time = 0

        # Start timing
        total_start_time = time.time()

        self.stdout.write(self.style.SUCCESS("Starting to seed breeds..."))
        self.stdout.write(
            f"Image fetching is {'disabled' if self.skip_images else 'enabled'}, "
            f"concurrency: {self.concurrency}, rate limit: {self.rate_limit}s"
        )

        # Clear existing breeds if needed (synchronous operation)
        if options.get("clear", False):
            with transaction.atomic():
                Breed.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("Cleared existing breeds"))

        # Fetch breed data using async operations
        loop = asyncio.get_event_loop()
        dog_breeds_data, cat_breeds_data = loop.run_until_complete(
            self.fetch_breed_data()
        )

        # Start image processing thread if needed
        if not self.skip_images:
            self.logger.info("Starting image processing thread")
            self.processing_complete.clear()
            image_processor = threading.Thread(
                target=self.process_image_queue, daemon=True
            )
            image_processor.start()

        # Process dog breeds (synchronous database operations)
        dog_start_time = time.time()
        dog_breeds = []
        if dog_breeds_data:
            # Create breeds
            dog_breeds = self.create_dog_breeds(dog_breeds_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(dog_breeds)} dog breeds in {time.time() - dog_start_time:.2f} seconds"
                )
            )

            # Download images if needed
            if not self.skip_images and dog_breeds:
                image_start_time = time.time()
                self.stdout.write(f"Downloading {len(dog_breeds)} dog breed images...")

                # Download images asynchronously and queue for processing
                loop.run_until_complete(self.download_dog_breed_images(dog_breeds))

                # Print status
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Queued dog breed images in {time.time() - image_start_time:.2f} seconds"
                    )
                )
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch dog breeds data"))

        # Process cat breeds (synchronous database operations)
        cat_start_time = time.time()
        cat_breeds = []
        if cat_breeds_data:
            # Create breeds
            cat_breeds = self.create_cat_breeds(cat_breeds_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(cat_breeds)} cat breeds in {time.time() - cat_start_time:.2f} seconds"
                )
            )

            # Download images if needed
            if not self.skip_images and cat_breeds:
                image_start_time = time.time()
                self.stdout.write(f"Downloading {len(cat_breeds)} cat breed images...")

                # Download images asynchronously and queue for processing
                loop.run_until_complete(self.download_cat_breed_images(cat_breeds))

                # Print status
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Queued cat breed images in {time.time() - image_start_time:.2f} seconds"
                    )
                )
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch cat breeds data"))

        # Wait for all image processing to complete
        if not self.skip_images and (dog_breeds or cat_breeds):
            try:
                total_count = len(dog_breeds) + len(cat_breeds)
                self.stdout.write(
                    f"Waiting for {total_count} images to be processed..."
                )

                # Wait for the queue to be empty and all processing to complete
                waiting_start = time.time()

                # Wait for the queue to be processed
                while (
                    not self.image_queue.empty() and time.time() - waiting_start < 300
                ):  # 5 minute timeout
                    self.stdout.write(
                        f"Queue size: {self.image_queue.qsize()}. Waiting..."
                    )
                    time.sleep(5)

                # Signal thread to complete
                self.processing_complete.set()

                # Wait for thread to join if it exists
                if image_processor.is_alive():
                    image_processor.join(timeout=10)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Image processing complete: {self.successful_images} successful, {self.failed_images} failed"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error waiting for image processing: {str(e)}")
                )

        # Total dog and cat breeds
        total_breeds = len(self.get_existing_breeds(Species.DOG)) + len(
            self.get_existing_breeds(Species.CAT)
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully completed breed seeding in {time.time() - total_start_time:.2f} seconds. "
                f"Total breeds in database: {total_breeds}"
            )
        )

    def process_image_queue(self):
        """Worker thread to process saved images in a synchronous context"""
        self.logger.info("Image processor thread started")

        while not (self.image_queue.empty() and self.processing_complete.is_set()):
            try:
                # Get next item from queue with a timeout to allow checking for completion
                try:
                    breed, image_content, file_name = self.image_queue.get(timeout=2)
                    self.logger.debug(
                        f"Processing image for {breed.name}, queue size: {self.image_queue.qsize()}"
                    )
                except queue.Empty:
                    # Check if we should exit
                    if self.processing_complete.is_set():
                        self.logger.info("Processing complete flag set, exiting thread")
                        break
                    continue

                try:
                    # Save image to breed (synchronous operation)
                    breed.image.save(file_name, ContentFile(image_content), save=True)
                    self.successful_images += 1

                    # Print progress every 5 images
                    if self.successful_images % 5 == 0:
                        self.stdout.write(
                            f"Saved {self.successful_images} images so far..."
                        )

                except Exception as e:
                    self.failed_images += 1
                    self.logger.error(f"Error saving image for {breed.name}: {str(e)}")
                    self.stdout.write(
                        self.style.WARNING(
                            f"Error saving image for {breed.name}: {str(e)}"
                        )
                    )

                # Mark task as done
                self.image_queue.task_done()

            except Exception as e:
                self.logger.error(f"Unexpected error in image processor: {str(e)}")

        self.logger.info(
            f"Image processor thread ending. Successful: {self.successful_images}, Failed: {self.failed_images}"
        )

    async def fetch_breed_data(self) -> tuple:
        """
        Asynchronously fetches both dog and cat breed data
        """
        async with aiohttp.ClientSession() as session:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.concurrency)

            # Fetch dog and cat breed data concurrently
            dog_task = self._fetch_dog_breeds(session, semaphore)
            cat_task = self._fetch_cat_breeds(session, semaphore)

            # Wait for both tasks to complete
            return await asyncio.gather(dog_task, cat_task)

    async def _fetch_dog_breeds(
        self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore
    ) -> List[Dict[str, Any]]:
        """
        Fetches dog breeds from TheDogAPI
        Returns processed breed data ready for creation
        """
        self.stdout.write("Fetching dog breeds from TheDogAPI...")
        try:
            headers = {"x-api-key": DOGS_API_KEY} if DOGS_API_KEY else {}

            await self._respect_rate_limit(self.dog_api_lock, True)

            async with semaphore:
                async with session.get(
                    "https://api.thedogapi.com/v1/breeds", headers=headers
                ) as response:
                    # Update last request time
                    self.last_dog_request_time = time.time()

                    if response.status != 200:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to fetch dog breeds: {response.status}"
                            )
                        )
                        return []

                    try:
                        dog_breeds_data = await response.json()
                        self.logger.debug(
                            f"Received {len(dog_breeds_data) if isinstance(dog_breeds_data, list) else 'non-list'} dog breeds"
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error parsing dog breeds response: {str(e)}"
                            )
                        )
                        return []

            if not dog_breeds_data or not isinstance(dog_breeds_data, list):
                self.stdout.write(self.style.ERROR("Invalid response from TheDogAPI"))
                return []

            # Process the breeds - similar format to TheCatAPI
            breeds_to_create = []

            for breed_data in dog_breeds_data:
                breed_id = breed_data.get("id")
                breed_name = breed_data.get("name")

                if not breed_id or not breed_name:
                    continue

                breed = {
                    "name": breed_name,
                    "species": Species.DOG,
                    "api_id": str(breed_id),
                }
                if "temperament" in breed_data:
                    breed["description"] = breed_data["temperament"]

                if "origin" in breed_data:
                    breed["origin"] = breed_data["origin"]

                if "life_span" in breed_data:
                    breed["life_span"] = breed_data["life_span"].replace(" years", "")

                if "weight" in breed_data and "metric" in breed_data["weight"]:
                    breed["weight"] = breed_data["weight"]["metric"]

                breeds_to_create.append(breed)

            # Sort breeds by name for consistency
            breeds_to_create.sort(key=lambda x: x["name"])

            return breeds_to_create

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching dog breeds: {str(e)}"))
            return []

    async def _fetch_cat_breeds(
        self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore
    ) -> List[Dict[str, Any]]:
        """
        Fetches cat breeds from TheCatAPI
        Returns raw API response data for processing
        """
        self.stdout.write("Fetching cat breeds from TheCatAPI...")
        try:
            headers = {"x-api-key": CATS_API_KEY} if CATS_API_KEY else {}

            await self._respect_rate_limit(self.cat_api_lock)

            async with semaphore:
                async with session.get(
                    "https://api.thecatapi.com/v1/breeds", headers=headers
                ) as response:
                    # Update last request time
                    self.last_cat_request_time = time.time()

                    if response.status != 200:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to fetch cat breeds: {response.status}"
                            )
                        )
                        return []

                    try:
                        cat_breeds = await response.json()
                        self.logger.debug(
                            f"Received {len(cat_breeds) if isinstance(cat_breeds, list) else 'non-list'} cat breeds"
                        )
                        return cat_breeds
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error parsing cat breeds response: {str(e)}"
                            )
                        )
                        return []

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching cat breeds: {str(e)}"))
            return []

    async def _respect_rate_limit(self, lock: asyncio.Lock, is_dog_api: bool = False):
        """
        Ensures rate limits are respected for API requests
        Adds some jitter to prevent synchronized requests
        """
        async with lock:
            last_request_time = (
                self.last_dog_request_time if is_dog_api else self.last_cat_request_time
            )
            current_time = time.time()

            # Calculate how long we need to wait
            elapsed = current_time - last_request_time
            if elapsed < MIN_REQUEST_INTERVAL:
                # Add some jitter to prevent all requests hitting at once
                jitter = random.uniform(0, MAX_REQUEST_INTERVAL - MIN_REQUEST_INTERVAL)
                wait_time = MIN_REQUEST_INTERVAL - elapsed + jitter

                if wait_time > 0:
                    self.logger.debug(
                        f"Rate limiting: waiting {wait_time:.2f}s for {'dog' if is_dog_api else 'cat'} API"
                    )
                    await asyncio.sleep(wait_time)

    def create_dog_breeds(
        self, breeds_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Creates dog breeds in the database and returns a list of created breeds with their API IDs
        This is a synchronous operation using Django's ORM
        """
        breeds_created = []
        existing_breeds = self.get_existing_breeds(Species.DOG)

        # Create breeds in a transaction for consistency
        with transaction.atomic():
            for breed_data in breeds_data:
                breed_name = breed_data["name"]
                api_id = breed_data.pop("api_id", "")

                # Skip if breed already exists
                if breed_name in existing_breeds:
                    self.stdout.write(
                        f"Dog breed '{breed_name}' already exists, skipping."
                    )
                    continue

                # Create breed instance
                breed = Breed(**breed_data, is_active=True)

                # Save the breed to generate an ID (required for image association)
                breed.save()

                self.logger.debug(f"Created dog breed: {breed_name} (ID: {breed.id})")

                # Add breed and API ID to the list for image downloads
                breeds_created.append({"breed": breed, "api_id": api_id})

        return breeds_created

    def create_cat_breeds(
        self, breeds_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Creates cat breeds in the database and returns a list of created breeds with their API IDs
        This is a synchronous operation using Django's ORM
        """
        breeds_created = []
        existing_breeds = self.get_existing_breeds(Species.CAT)

        # Create breeds in a transaction for consistency
        with transaction.atomic():
            for breed_data in breeds_data:
                breed_name = breed_data.get("name", "")
                breed_id = breed_data.get("id", "")

                if not breed_name or not breed_id:
                    continue

                # Skip if breed already exists
                if breed_name in existing_breeds:
                    self.stdout.write(
                        f"Cat breed '{breed_name}' already exists, skipping."
                    )
                    continue

                breed_info = {
                    "name": breed_name,
                    "species": Species.CAT,
                    "is_active": True,
                }

                if "description" in breed_data:
                    breed_info["description"] = breed_data["description"]

                if "origin" in breed_data:
                    breed_info["origin"] = breed_data["origin"]

                if "life_span" in breed_data:
                    breed_info["life_span"] = breed_data["life_span"]

                if "weight" in breed_data and "metric" in breed_data["weight"]:
                    breed_info["weight"] = breed_data["weight"]["metric"]

                breed = Breed(**breed_info)

                # Save the breed to generate an ID (required for image association)
                breed.save()

                self.logger.debug(f"Created cat breed: {breed_name} (ID: {breed.id})")

                # Add breed and API ID to the list for image downloads
                breeds_created.append({"breed": breed, "api_id": breed_id})

        return breeds_created

    async def download_dog_breed_images(self, breeds: List[Dict[str, Any]]) -> None:
        """
        Downloads images for dog breeds asynchronously and adds them to the processing queue
        """
        self.logger.info(f"Starting to download {len(breeds)} dog breed images")

        async with aiohttp.ClientSession() as session:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.concurrency)

            # Create tasks for downloading images
            tasks = []
            for breed_info in breeds:
                tasks.append(
                    self._download_dog_image(
                        session, semaphore, breed_info["breed"], breed_info["api_id"]
                    )
                )

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log the results
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                self.logger.warning(
                    f"Got {len(exceptions)} exceptions while downloading dog images"
                )
                for e in exceptions[:5]:  # Log first 5 exceptions
                    self.logger.warning(f"Download exception: {str(e)}")

        self.logger.info("Completed downloading dog breed images")

    async def download_cat_breed_images(self, breeds: List[Dict[str, Any]]) -> None:
        """
        Downloads images for cat breeds asynchronously and adds them to the processing queue
        """
        self.logger.info(f"Starting to download {len(breeds)} cat breed images")

        async with aiohttp.ClientSession() as session:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.concurrency)

            # Create tasks for downloading images
            tasks = []
            for breed_info in breeds:
                tasks.append(
                    self._download_cat_image(
                        session, semaphore, breed_info["breed"], breed_info["api_id"]
                    )
                )

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log the results
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                self.logger.warning(
                    f"Got {len(exceptions)} exceptions while downloading cat images"
                )
                for e in exceptions[:5]:  # Log first 5 exceptions
                    self.logger.warning(f"Download exception: {str(e)}")

        self.logger.info("Completed downloading cat breed images")

    async def _download_dog_image(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        breed: Breed,
        api_id: str,
    ) -> None:
        """
        Downloads an image for a dog breed and adds it to the queue for processing
        """
        try:
            self.logger.debug(
                f"Downloading image for dog breed: {breed.name} (ID: {api_id})"
            )

            # Get image content
            image_content = await self._get_dog_breed_image(session, semaphore, api_id)
            if not image_content:
                self.logger.warning(
                    f"Could not get image content for dog breed {breed.name}"
                )
                return

            # Add to processing queue (will be handled by synchronous thread)
            file_name = f"{breed.name.lower().replace(' ', '_')}.jpg"
            self.logger.debug(f"Adding dog image for {breed.name} to processing queue")
            self.image_queue.put((breed, image_content, file_name))
            self.logger.debug(
                f"Current queue size after adding dog image: {self.image_queue.qsize()}"
            )

        except Exception as e:
            self.logger.error(f"Error downloading image for dog {breed.name}: {str(e)}")
            self.stdout.write(
                self.style.WARNING(
                    f"Error downloading image for {breed.name}: {str(e)}"
                )
            )

    async def _download_cat_image(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        breed: Breed,
        api_id: str,
    ) -> None:
        """
        Downloads an image for a cat breed and adds it to the queue for processing
        """
        try:
            self.logger.debug(
                f"Downloading image for cat breed: {breed.name} (ID: {api_id})"
            )

            # Get image content
            image_content = await self._get_cat_breed_image(session, semaphore, api_id)
            if not image_content:
                self.logger.warning(
                    f"Could not get image content for cat breed {breed.name}"
                )
                return

            # Add to processing queue (will be handled by synchronous thread)
            file_name = f"{breed.name.lower().replace(' ', '_')}.jpg"
            self.logger.debug(f"Adding cat image for {breed.name} to processing queue")
            self.image_queue.put((breed, image_content, file_name))
            self.logger.debug(
                f"Current queue size after adding cat image: {self.image_queue.qsize()}"
            )

        except Exception as e:
            self.logger.error(f"Error downloading image for cat {breed.name}: {str(e)}")
            self.stdout.write(
                self.style.WARNING(
                    f"Error downloading image for {breed.name}: {str(e)}"
                )
            )

    async def _get_dog_breed_image(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        breed_id: str,
    ) -> Optional[bytes]:
        """
        Fetches an image for a dog breed from TheDogAPI
        Returns the image content as bytes if successful, None otherwise
        """
        headers = {"x-api-key": DOGS_API_KEY} if DOGS_API_KEY else {}

        for attempt in range(self.retry_count):
            try:
                # Respect rate limits
                await self._respect_rate_limit(self.dog_api_lock, True)

                self.logger.debug(f"Fetching image for dog breed ID: {breed_id}")
                async with semaphore:
                    # Use the same approach as for cats
                    async with session.get(
                        "https://api.thedogapi.com/v1/images/search",
                        params={"breed_ids": breed_id, "limit": 1},
                        headers=headers,
                    ) as response:
                        # Update last request time
                        self.last_dog_request_time = time.time()

                        if response.status == 429:  # Too Many Requests
                            self.logger.warning(
                                f"Rate limit hit for dog breed {breed_id}. Waiting longer..."
                            )
                            # Exponential backoff
                            await asyncio.sleep(MIN_REQUEST_INTERVAL * (2**attempt))
                            continue

                        if response.status != 200:
                            self.logger.warning(
                                f"Failed to fetch dog image for {breed_id}: Status {response.status}"
                            )
                            await asyncio.sleep(1)
                            continue

                        try:
                            data = await response.json()
                            self.logger.debug(
                                f"Dog image search response for {breed_id}: {data}"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error parsing dog image response for {breed_id}: {str(e)}"
                            )
                            await asyncio.sleep(1)
                            continue

                if not data or not isinstance(data, list) or len(data) == 0:
                    self.logger.warning(f"No results returned for dog breed {breed_id}")
                    await asyncio.sleep(1)
                    continue

                image_url = data[0].get("url")
                if not image_url:
                    self.logger.warning(
                        f"No image URL in response for dog breed {breed_id}"
                    )
                    await asyncio.sleep(1)
                    continue

                # Respect rate limits before downloading the image
                await self._respect_rate_limit(self.dog_api_lock, True)

                # Download the image
                self.logger.debug(f"Downloading dog image from URL: {image_url}")
                async with semaphore:
                    async with session.get(image_url) as image_response:
                        # Update last request time
                        self.last_dog_request_time = time.time()

                        if image_response.status != 200:
                            self.logger.warning(
                                f"Failed to download dog image for {breed_id}: Status {image_response.status}"
                            )
                            await asyncio.sleep(1)
                            continue

                        image_content = await image_response.read()
                        self.logger.debug(
                            f"Downloaded dog image for {breed_id}, size: {len(image_content)} bytes"
                        )
                        return image_content

            except Exception as e:
                self.logger.error(
                    f"Error downloading dog image for {breed_id} (attempt {attempt+1}): {str(e)}"
                )
                await asyncio.sleep(1)

        self.logger.error(
            f"Failed to get image for dog breed {breed_id} after {self.retry_count} attempts"
        )
        return None

    async def _get_cat_breed_image(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        breed_id: str,
    ) -> Optional[bytes]:
        """
        Fetches a representative image for a cat breed from TheCatAPI
        Returns the image content as bytes if successful, None otherwise
        """
        headers = {"x-api-key": CATS_API_KEY} if CATS_API_KEY else {}

        for attempt in range(self.retry_count):
            try:
                # Respect rate limits
                await self._respect_rate_limit(self.cat_api_lock)

                self.logger.debug(f"Fetching image for cat breed ID: {breed_id}")
                async with semaphore:
                    # Use the exact URL and parameters as requested
                    async with session.get(
                        "https://api.thecatapi.com/v1/images/search",
                        params={"breed_ids": breed_id, "limit": 1},
                        headers=headers,
                    ) as response:
                        # Update last request time
                        self.last_cat_request_time = time.time()

                        if response.status == 429:  # Too Many Requests
                            self.logger.warning(
                                f"Rate limit hit for cat breed {breed_id}. Waiting longer..."
                            )
                            # Exponential backoff
                            await asyncio.sleep(MIN_REQUEST_INTERVAL * (2**attempt))
                            continue

                        if response.status != 200:
                            self.logger.warning(
                                f"Failed to fetch cat image for {breed_id}: Status {response.status}"
                            )
                            await asyncio.sleep(1)
                            continue

                        try:
                            data = await response.json()
                            self.logger.debug(
                                f"Cat image search response for {breed_id}: {data}"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error parsing cat image response for {breed_id}: {str(e)}"
                            )
                            await asyncio.sleep(1)
                            continue

                if not data or not isinstance(data, list) or len(data) == 0:
                    self.logger.warning(f"No results returned for cat breed {breed_id}")
                    await asyncio.sleep(1)
                    continue

                image_url = data[0].get("url")
                if not image_url:
                    self.logger.warning(
                        f"No image URL in response for cat breed {breed_id}"
                    )
                    await asyncio.sleep(1)
                    continue

                # Respect rate limits before downloading the image
                await self._respect_rate_limit(self.cat_api_lock)

                # Download the image
                self.logger.debug(f"Downloading cat image from URL: {image_url}")
                async with semaphore:
                    async with session.get(image_url) as image_response:
                        # Update last request time
                        self.last_cat_request_time = time.time()

                        if image_response.status != 200:
                            self.logger.warning(
                                f"Failed to download cat image for {breed_id}: Status {image_response.status}"
                            )
                            await asyncio.sleep(1)
                            continue

                        image_content = await image_response.read()
                        self.logger.debug(
                            f"Downloaded cat image for {breed_id}, size: {len(image_content)} bytes"
                        )
                        return image_content

            except Exception as e:
                self.logger.error(
                    f"Error downloading cat image for {breed_id} (attempt {attempt+1}): {str(e)}"
                )
                await asyncio.sleep(1)

        self.logger.error(
            f"Failed to get image for cat breed {breed_id} after {self.retry_count} attempts"
        )
        return None

    def get_existing_breeds(self, species: str) -> Set[str]:
        """
        Returns a set of existing breed names for the specified species
        """
        return set(Breed.objects.filter(species=species).values_list("name", flat=True))
