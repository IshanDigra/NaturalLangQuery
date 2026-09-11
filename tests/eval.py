import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.fallback_parser import parse_fallback
from app.llm_parser import parse_llm

def evaluate():
    with open("tests/eval_queries.json", "r") as f:
        cases = json.load(f)

    use_llm = "--llm" in sys.argv

    total = len(cases)
    passed = 0

    for case in cases:
        query = case["query"]
        expected = case["expected"]

        if use_llm:
            result_obj = parse_llm(query)
            if not result_obj:
                print(f"[{query}] FAILED: LLM parser returned None")
                continue
        else:
            result_obj = parse_fallback(query)

        result_dict = result_obj.model_dump(exclude_none=True)

        # Check if all expected keys/values are in the result
        case_passed = True
        for k, v in expected.items():
            if k not in result_dict:
                case_passed = False
                print(f"[{query}] FAILED: missing key {k}")
                break

            res_v = result_dict[k]

            # handle enums comparison
            if isinstance(v, list):
                res_v_str = [str(x.value) if hasattr(x, 'value') else str(x) for x in res_v]
                for ev in v:
                    if ev not in res_v_str:
                        case_passed = False
                        print(f"[{query}] FAILED: {k} missing value {ev}. Got: {res_v_str}")
                        break
            else:
                if res_v != v:
                    case_passed = False
                    print(f"[{query}] FAILED: {k} mismatch. Expected {v}, got {res_v}")
                    break

        if case_passed:
            passed += 1
            print(f"[{query}] PASSED")

    pass_rate = (passed / total) * 100
    print(f"\nPass rate: {pass_rate:.1f}% ({passed}/{total})")

if __name__ == "__main__":
    evaluate()
