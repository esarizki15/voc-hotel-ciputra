from engine.ollama_client import (
    OllamaABSAClient,
)


class AnalysisService:

    def __init__(
        self,
        ollama_client: OllamaABSAClient,
    ):

        self.ollama_client = (
            ollama_client
        )

    def analyze_review(
        self,
        review_text: str,
    ):

        return (
            self.ollama_client
            .analyze_review(
                review_text
            )
        )

    def analyze_reviews(
        self,
        reviews: list[str],
    ):

        results = []

        for review in reviews:

            aspects = (
                self.analyze_review(
                    review
                )
            )

            results.append(
                {
                    "review_text": review,
                    "aspects": aspects,
                }
            )

        return results