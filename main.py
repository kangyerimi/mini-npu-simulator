import json
import os
import time

EPSILON = 1e-9   # 허용오차: 두 점수 차이가 이보다 작으면 동점으로 본다
REPEAT = 10      # 시간 측정 반복 횟수
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


# ==========================================================
# 1. 핵심 연산: MAC, 판정, 시간 측정
# ==========================================================
def mac(pattern, filt):
    """패턴과 필터를 같은 칸끼리 곱하고 모두 더한 점수를 돌려준다."""
    n = len(pattern)          # 표의 크기 (3x3이면 3)
    total = 0.0               # 점수를 모아둘 곳. 0에서 시작
    for i in range(n):        # i = 줄 번호: 0, 1, ..., n-1
        for j in range(n):    # j = 칸 번호: 0, 1, ..., n-1
            total += pattern[i][j] * filt[i][j]   # 곱해서(Multiply) 누적(Accumulate)
    return total


def judge(score_a, score_b):
    """두 점수를 비교해 "A", "B", "UNDECIDED"(동점) 중 하나를 돌려준다."""
    if abs(score_a - score_b) < EPSILON:   # 차이가 거의 없으면 동점
        return "UNDECIDED"
    if score_a > score_b:
        return "A"
    return "B"


def measure_mac(pattern, filt, func=mac):
    """MAC 연산(func)을 REPEAT번 반복해서 평균 시간(ms)을 돌려준다."""
    func(pattern, filt)                    # 준비 운동 1회 (측정에 넣지 않음)
    total_time = 0.0
    for _ in range(REPEAT):
        start = time.perf_counter()        # 시작 시각
        func(pattern, filt)                # 재려는 연산만 실행 (입출력 제외)
        end = time.perf_counter()          # 끝 시각
        total_time += end - start
    return total_time / REPEAT * 1000      # 초 -> 밀리초(ms)


# ==========================================================
# ★ 보너스 1. 1차원 배열 최적화
# ==========================================================
def flatten(matrix):
    """2차원 표를 한 줄로 길게 이어 붙인 1차원 리스트(길이 N²)로 바꾼다."""
    flat = []
    for row in matrix:                     # 한 줄씩 꺼내서
        for value in row:                  # 그 줄의 값을 차례로
            flat.append(value)             # 뒤에 이어 붙인다
    return flat


def mac_flat(pattern_flat, filter_flat):
    """1차원으로 펼친 패턴과 필터로 MAC 점수를 계산한다. 반복문이 한 겹이다."""
    total = 0.0
    for k in range(len(pattern_flat)):     # k = 0, 1, ..., N²-1
        total += pattern_flat[k] * filter_flat[k]
    return total


def print_flat_comparison(sizes):
    """같은 입력, 같은 반복 횟수로 2차원 방식과 1차원 방식의 시간을 비교한다."""
    print("크기        2차원(ms)     1차원(ms)     시간 비율    점수 일치")
    print("------------------------------------------------------------------")
    for n in sizes:
        pattern = make_cross(n)
        filt = make_cross(n)
        pattern_flat = flatten(pattern)    # 변환은 측정 전에 한 번만 해 둔다
        filter_flat = flatten(filt)

        time_2d = measure_mac(pattern, filt, mac)
        time_1d = measure_mac(pattern_flat, filter_flat, mac_flat)
        same = abs(mac(pattern, filt) - mac_flat(pattern_flat, filter_flat)) < EPSILON

        size_text = f"{n}x{n}"
        ratio_text = f"{time_1d / time_2d * 100:.0f}%"
        same_text = "일치" if same else "불일치"
        print(f"{size_text:<10}  {time_2d:<12.6f}  {time_1d:<12.6f}  {ratio_text:<11}  {same_text}")
    print("(시간 비율 = 1차원 시간 / 2차원 시간. 100%보다 작으면 1차원이 더 빠름)")


# ==========================================================
# 2. 패턴 생성기: 크기 n의 십자가 / X 모양을 자동으로 만든다
# ==========================================================
def make_cross(n):
    """n x n 십자가 패턴: 가운데 줄과 가운데 칸이 1."""
    mid = n // 2
    return [[1.0 if i == mid or j == mid else 0.0 for j in range(n)] for i in range(n)]


def make_x(n):
    """n x n X 패턴: 두 대각선이 1."""
    return [[1.0 if i == j or i + j == n - 1 else 0.0 for j in range(n)] for i in range(n)]


# ==========================================================
# 3. 화면 출력 도우미
# ==========================================================
def print_header(title):
    print()
    print("#---------------------------------------")
    print(f"# {title}")
    print("#---------------------------------------")


def print_matrix(matrix):
    """표를 한 줄씩 보기 좋게 출력한다."""
    for row in matrix:
        print("  " + " ".join(str(v) for v in row))


def print_performance(sizes):
    """크기별로 MAC 평균 시간과 연산 횟수(N²)를 표로 출력한다."""
    print("크기        평균 시간(ms)    연산 횟수(N²)")
    print("------------------------------------------")
    for n in sizes:
        pattern = make_cross(n)            # 생성기로 만든 패턴을 재활용
        filt = make_cross(n)
        avg_ms = measure_mac(pattern, filt)
        size_text = f"{n}x{n}"
        print(f"{size_text:<10}  {avg_ms:<15.6f}  {n * n}")


# ==========================================================
# 4. 모드 1: 사용자 입력 (3x3)
# ==========================================================
def read_matrix(name, n):
    """키보드로 n줄을 입력받아 n x n 표를 만든다. 잘못된 줄은 다시 입력받는다."""
    print(f"{name} ({n}줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < n:                 # n줄이 모일 때까지 반복
        parts = input().split()            # 한 줄을 공백으로 나눈다
        if len(parts) != n:                # 숫자 개수가 틀린 경우
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
            continue                       # 이 줄을 다시 입력받는다
        try:
            row = [float(p) for p in parts]   # 글자를 숫자로 바꾼다
        except ValueError:                 # 숫자가 아닌 글자가 섞인 경우
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
            continue
        matrix.append(row)                 # 올바른 줄만 저장
    return matrix


def mode_user_input():
    """모드 1: 3x3 필터 2개와 패턴을 직접 입력받아 판정한다."""
    n = 3

    print_header("[1] 필터 입력")
    filter_a = read_matrix("필터 A", n)
    print()
    filter_b = read_matrix("필터 B", n)

    print()
    print("필터 저장 확인")
    print("필터 A:")
    print_matrix(filter_a)
    print("필터 B:")
    print_matrix(filter_b)

    print_header("[2] 패턴 입력")
    pattern = read_matrix("패턴", n)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = measure_mac(pattern, filter_a)
    result = judge(score_a, score_b)

    print_header("[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.6f} ms")
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    print_header(f"[4] 성능 분석 (평균/{REPEAT}회)")
    print_performance([3])


# ==========================================================
# 5. 모드 2: data.json 분석
# ==========================================================
def normalize_label(raw):
    """여러 표기('+', 'cross', 'x' 등)를 표준 라벨 Cross / X 로 통일한다."""
    if not isinstance(raw, str):
        return None
    text = raw.strip().lower()             # 앞뒤 공백 제거, 소문자로 통일
    if text in ("+", "cross"):
        return "Cross"
    if text == "x":
        return "X"
    return None                            # 모르는 라벨


def is_square_matrix(matrix, n):
    """matrix가 숫자로만 이루어진 n x n 표인지 확인한다."""
    if not isinstance(matrix, list) or len(matrix) != n:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
    return True


def load_filters(data):
    """filters를 읽어 {크기: {"Cross": 표, "X": 표}} 형태로 정리한다."""
    filters = {}
    raw_filters = data.get("filters")
    if not isinstance(raw_filters, dict):
        print("✗ filters 항목이 없거나 형식이 잘못되었습니다.")
        return filters

    for key, group in raw_filters.items():
        parts = key.split("_")             # "size_13" -> ["size", "13"]
        if len(parts) != 2 or parts[0] != "size" or not parts[1].isdigit():
            print(f"✗ {key}: 필터 키 형식 오류 (size_N 형태여야 함)")
            continue
        n = int(parts[1])
        if not isinstance(group, dict):
            print(f"✗ {key}: 필터 내용 형식 오류")
            continue

        normalized = {}
        for label, matrix in group.items():
            std = normalize_label(label)   # 'cross' -> Cross, 'x' -> X
            if std is not None and is_square_matrix(matrix, n):
                normalized[std] = matrix

        if "Cross" in normalized and "X" in normalized:
            filters[n] = normalized
            print(f"✓ {key} 필터 로드 완료 (Cross, X)")
        else:
            print(f"✗ {key}: Cross/X 필터가 없거나 크기가 {n}x{n}이 아닙니다.")
    return filters


def analyze_pattern(key, item, filters):
    """패턴 1개를 판정한다. (통과 여부, 실패 사유)를 돌려준다."""
    # 1) 키에서 크기 N 꺼내기: "size_13_2" -> 13
    parts = key.split("_")
    if len(parts) != 3 or parts[0] != "size" or not parts[1].isdigit():
        reason = "키 형식 오류 (size_N_idx 형태여야 함)"
        print(f"판정: - | FAIL ({reason})")
        return False, reason
    n = int(parts[1])

    # 2) 맞는 크기의 필터가 있는지
    if n not in filters:
        reason = f"size_{n} 필터 없음"
        print(f"판정: - | FAIL ({reason})")
        return False, reason

    # 3) 패턴 내용과 크기 검증
    if not isinstance(item, dict) or "input" not in item or "expected" not in item:
        reason = "input 또는 expected 항목 없음"
        print(f"판정: - | FAIL ({reason})")
        return False, reason
    pattern = item["input"]
    if not is_square_matrix(pattern, n):
        reason = f"크기 불일치 (패턴이 {n}x{n} 숫자 표가 아님)"
        print(f"판정: - | FAIL ({reason})")
        return False, reason

    # 4) 정답 라벨 정규화: '+' -> Cross, 'x' -> X
    expected = normalize_label(item["expected"])
    if expected is None:
        reason = f"알 수 없는 expected 라벨: {item['expected']!r}"
        print(f"판정: - | FAIL ({reason})")
        return False, reason

    # 5) MAC 연산과 판정
    score_cross = mac(pattern, filters[n]["Cross"])
    score_x = mac(pattern, filters[n]["X"])
    result = judge(score_cross, score_x)   # A = Cross, B = X
    if result == "A":
        decision = "Cross"
    elif result == "B":
        decision = "X"
    else:
        decision = "UNDECIDED"

    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")

    # 6) 정답과 비교
    if decision == expected:
        print(f"판정: {decision} | expected: {expected} | PASS")
        return True, ""
    if decision == "UNDECIDED":
        reason = f"동점(UNDECIDED): 점수 차이가 epsilon({EPSILON}) 미만"
        print(f"판정: {decision} | expected: {expected} | FAIL (동점 규칙)")
    else:
        reason = f"판정 {decision} != expected {expected}"
        print(f"판정: {decision} | expected: {expected} | FAIL (판정 불일치)")
    return False, reason


def mode_json():
    """모드 2: data.json의 모든 패턴을 판정하고 결과를 요약한다."""
    # 파일 읽기: 실패해도 프로그램이 죽지 않게 처리
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: data.json 파일을 찾을 수 없습니다. ({DATA_FILE})")
        return
    except json.JSONDecodeError as error:
        print(f"오류: data.json 형식이 잘못되었습니다. ({error})")
        return
    if not isinstance(data, dict):
        print("오류: data.json의 최상위 구조가 잘못되었습니다.")
        return

    print_header("[1] 필터 로드")
    filters = load_filters(data)

    print_header("[2] 패턴 분석 (라벨 정규화 적용)")
    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("patterns 항목이 없거나 형식이 잘못되었습니다.")
        patterns = {}

    total = 0
    passed = 0
    failures = []                          # (케이스 이름, 실패 사유) 목록
    for key, item in patterns.items():
        print(f"--- {key} ---")
        total += 1
        ok, reason = analyze_pattern(key, item, filters)
        if ok:
            passed += 1
        else:
            failures.append((key, reason))

    print_header(f"[3] 성능 분석 (평균/{REPEAT}회)")
    print_performance([3, 5, 13, 25])

    print_header(f"[3-2] 보너스: 2차원 vs 1차원 비교 (평균/{REPEAT}회)")
    print_flat_comparison([3, 5, 13, 25])

    print_header("[4] 결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")
    if failures:
        print()
        print("실패 케이스:")
        for key, reason in failures:
            print(f"- {key}: {reason}")
    print('(상세 원인 분석 및 복잡도 설명은 README.md의 "결과 리포트" 섹션에 작성)')


# ==========================================================
# 6. 프로그램 시작점
# ==========================================================
def main():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            mode_user_input()
            break
        if choice == "2":
            mode_json()
            break
        print("입력 오류: 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()