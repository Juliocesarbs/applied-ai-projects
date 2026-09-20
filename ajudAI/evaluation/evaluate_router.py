import time
from collections.abc import Callable

from sklearn.metrics import accuracy_score, classification_report

from evaluation.dataset import DEVELOPMENT_DATASET, TEST_DATASET
from src.router.llm_router import route_message_with_llm
from src.router.router import route_message


Dataset = list[tuple[str, str]]


def evaluate_router(
    name: str,
    router: Callable[[str], str],
    dataset: Dataset,
    show_progress: bool = False,
) -> None:
    expected = []
    predicted = []
    latencies = []

    total = len(dataset)

    for index, (message, expected_route) in enumerate(
        dataset,
        start=1,
    ):
        start = time.perf_counter()

        predicted_route = router(message)

        latency = time.perf_counter() - start

        expected.append(expected_route)
        predicted.append(predicted_route)
        latencies.append(latency)

        if show_progress:
            print(
                f"\rProcessing: {index}/{total}",
                end="",
                flush=True,
            )

    if show_progress:
        print()

    accuracy = accuracy_score(expected, predicted)
    average_latency = sum(latencies) / len(latencies)

    print(f"\n{name}")
    print("-" * 50)
    print(f"Samples: {len(dataset)}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Average latency: {average_latency:.3f}s")

    print("\nClassification report:")
    print(
        classification_report(
            expected,
            predicted,
            digits=3,
            zero_division=0,
        )
    )

    errors = [
        (message, expected_route, predicted_route)
        for (message, expected_route), predicted_route
        in zip(dataset, predicted)
        if expected_route != predicted_route
    ]

    if errors:
        print(f"\nErrors ({len(errors)}):")
        print("-" * 50)

        for message, expected_route, predicted_route in errors:
            print(
                f"Expected: {expected_route} | "
                f"Predicted: {predicted_route}"
            )
            print(f"Message: {message}\n")
    else:
        print("\nNo classification errors.")


def main() -> None:
    print("\nTEST DATASET")

    evaluate_router(
        name="Rules Router",
        router=route_message,
        dataset=TEST_DATASET,
    )

    print("\nWarming up Qwen3 4B...")
    route_message_with_llm("Teste de inicialização")

    evaluate_router(
        name="Qwen3 4B Router",
        router=route_message_with_llm,
        dataset=TEST_DATASET,
        show_progress=True,
    )


if __name__ == "__main__":
    main()