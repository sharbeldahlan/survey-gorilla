""" Management command to simulate a number of conversations. """
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from openai import (
    APIError,
    APITimeoutError,
    RateLimitError,
)

from applications.surveys.services import simulate_conversation
from applications.logging import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    # pylint: disable=missing-class-docstring
    help = "Simulate survey conversations between AI agents"

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=100,
            help="Number of conversations to simulate",
        )

    def handle(self, *args, **options):
        """
        Runs the simulation for a given number of conversations,
        with rate limiting and specific exception handling.
        """
        total_conversations = options["count"]
        successful_simulations = 0
        failed_simulations = 0

        for current_conversation in range(1, total_conversations + 1):
            try:
                with transaction.atomic():
                    simulate_conversation()
                successful_simulations += 1

            except (RateLimitError, APIError, APITimeoutError) as error:
                logger.warning("OpenAI API error on conversation number %d: %s", current_conversation, error)
                failed_simulations += 1

            except Exception as error:  # pylint: disable=broad-exception-caught
                logger.error("Unexpected error on conversation number %d: %s", current_conversation, error)
                failed_simulations += 1

            if current_conversation % 10 == 0:
                self.stdout.write(f"Processed {current_conversation}/{total_conversations} conversations")

            time.sleep(0.5)

        self.stdout.write(
            self.style.SUCCESS(f"Finished simulations: {successful_simulations} succeeded, {failed_simulations} failed")
        )
