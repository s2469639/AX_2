// ─────────────────────────────────────────────────────────────
// 견적 요청 접수 API  (주소: /api/inquiries)
//
// 이 파일은 "화면"이 아니라 "창구"예요.
// 브라우저나 다른 프로그램이 이 주소로 요청을 보내면, 여기서 받아서 답을 돌려줘요.
//   - GET  = "목록 좀 보여 줘"  → (가상) 문의 3건을 돌려줌
//   - POST = "이거 접수해 줘"   → 설계서 ② 검사 규칙으로 확인한 뒤 결과를 돌려줌
//
// 설계서: backend-lab/02_로직설계/로직설계서_내기능.md
// ※ 아직 DB(데이터 창고)에는 저장하지 않아요. 저장은 다음 섹션에서 붙여요.
// ─────────────────────────────────────────────────────────────

// ── 고를 수 있는 값 목록 ─────────────────────────────────────
// 설계서 ①: 국가 · 상품 · 무역 조건은 "목록에서 선택"이에요.
// 목록에 없는 값이 오면 ② 검사에서 걸러 내요.
// 목록 자체는 화면(폼)과 함께 쓰려고 lib/inquiryOptions.ts 에 모아 뒀어요.
// (요청사항 최대 글자 수 MAX_MESSAGE_LENGTH 도 거기 있어요)
import { COUNTRIES, MAX_MESSAGE_LENGTH, PRODUCTS, TRADE_TERMS } from "@/lib/inquiryOptions";

// 이메일 모양 검사용 규칙: "글자@글자.글자" 꼴인지 확인해요.
// (진짜 있는 주소인지까지는 알 수 없어요. 모양만 봐요.)
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ── GET: (가상) 문의 3건 돌려주기 ────────────────────────────
// 실제 회사·사람 이름은 쓰지 않고, 모두 "(가상)"을 붙였어요.
export async function GET() {
  const sampleInquiries = [
    {
      receiptNo: "Q-20261116-0001",
      company: "(가상) 하늘상사",
      email: "buyer1@example.com", // example.com 은 연습용으로 정해진 가짜 주소예요
      country: "미국",
      product: "(가상) 샘플 상품 A",
      quantity: 500,
      dueDate: "2026-12-14",
      tradeTerm: "FOB",
      message: "(가상) 4주 안에 받을 수 있을까요?",
      status: "신규",
      receivedAt: "2026-11-16T09:10:00+09:00",
    },
    {
      receiptNo: "Q-20261116-0002",
      company: "(가상) 바다무역",
      email: "buyer2@example.com",
      country: "일본",
      product: "(가상) 샘플 상품 B",
      quantity: 1200,
      dueDate: null, // 희망 납기는 선택 칸이라 비어 있을 수 있어요
      tradeTerm: "CIF",
      message: "",
      status: "신규",
      receivedAt: "2026-11-16T10:25:00+09:00",
    },
    {
      receiptNo: "Q-20261116-0003",
      company: "(가상) 별빛트레이딩",
      email: "buyer3@example.com",
      country: "베트남",
      product: "(가상) 샘플 상품 C",
      quantity: 80,
      dueDate: "2027-01-05",
      tradeTerm: null, // 무역 조건도 선택 칸이에요
      message: "(가상) 포장 규격을 함께 알려 주세요.",
      status: "신규",
      receivedAt: "2026-11-16T11:40:00+09:00",
    },
  ];

  // Response.json(...) = 내용을 JSON(프로그램끼리 주고받는 표준 글 모양)으로 바꿔서 돌려줘요.
  return Response.json({ inquiries: sampleInquiries });
}

// ── POST: 견적 요청 받기 ─────────────────────────────────────
export async function POST(request: Request) {
  try {
    // 1) 보내온 내용을 꺼내요.
    //    내용이 JSON 모양이 아니면(깨진 글이면) 여기서 실패하니, 따로 잡아서 안내해요.
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return badRequest({ _form: "보낸 내용을 읽을 수 없어요. 입력한 내용을 확인해 주세요." });
    }

    // 내용이 "칸 이름: 값" 묶음(객체)이 아니면 더 볼 것도 없어요.
    if (typeof body !== "object" || body === null || Array.isArray(body)) {
      return badRequest({ _form: "보낸 내용을 읽을 수 없어요. 입력한 내용을 확인해 주세요." });
    }
    const data = body as Record<string, unknown>;

    // 2) 설계서 ② 검사 — 틀린 칸마다 안내 문구를 모아 둬요.
    //    (한 번에 모두 알려 줘야 사용자가 여러 번 고치지 않아도 돼요)
    const errors: Record<string, string> = {};

    // 글자 칸은 앞뒤 빈칸을 잘라 내고 봐요. ("   " 처럼 빈칸만 있으면 빈 칸으로 취급)
    const company = text(data.company);
    const email = text(data.email);
    const country = text(data.country);
    const product = text(data.product);
    const dueDate = text(data.dueDate);
    const tradeTerm = text(data.tradeTerm);
    const message = text(data.message);

    // ▸ 회사명 (필수)
    if (!company) errors.company = "회사명을 입력해 주세요.";

    // ▸ 이메일 (필수, 이메일 형식)
    if (!email) errors.email = "이메일을 입력해 주세요.";
    else if (!EMAIL_PATTERN.test(email)) errors.email = "이메일 주소를 확인해 주세요.";

    // ▸ 국가 (필수, 목록에서 선택)
    if (!country) errors.country = "국가를 입력해 주세요.";
    else if (!COUNTRIES.includes(country)) errors.country = "국가는 목록에서 골라 주세요.";

    // ▸ 상품 (필수, 목록에서 선택)
    if (!product) errors.product = "상품을 입력해 주세요.";
    else if (!PRODUCTS.includes(product)) errors.product = "상품은 목록에서 골라 주세요.";

    // ▸ 수량 (필수, 1 이상 정수)
    //   화면에서 숫자가 "500" 같은 글자로 올 수도 있어서 숫자로 바꿔 본 뒤 확인해요.
    const quantity = toNumber(data.quantity);
    if (quantity === undefined) errors.quantity = "수량을 입력해 주세요.";
    else if (!Number.isInteger(quantity) || quantity < 1)
      errors.quantity = "수량은 1개 이상의 정수로 입력해 주세요."; // 0, 음수, 소수(1.5) 모두 여기서 걸러요

    // ▸ 희망 납기 (선택, 오늘 이후 날짜)
    //   비어 있으면 통과. 값이 있으면 "2026-12-31" 모양인지, 지난 날짜가 아닌지 봐요.
    if (dueDate) {
      if (!isValidDate(dueDate)) errors.dueDate = "날짜를 2026-12-31 모양으로 입력해 주세요.";
      else if (dueDate < todayString()) errors.dueDate = "희망 납기는 오늘 이후 날짜를 골라 주세요.";
    }

    // ▸ 무역 조건 (선택, FOB / CIF / EXW 중 하나)
    if (tradeTerm && !TRADE_TERMS.includes(tradeTerm))
      errors.tradeTerm = "무역 조건은 FOB, CIF, EXW 중에서 골라 주세요.";

    // ▸ 요청사항 (선택, 1000자 이하)
    //   [...message].length 는 이모지 같은 특수 글자도 한 글자로 세는 방법이에요.
    if ([...message].length > MAX_MESSAGE_LENGTH)
      errors.message = `요청사항은 ${MAX_MESSAGE_LENGTH}자 이하로 써 주세요.`;

    // 3) 틀린 칸이 하나라도 있으면 → 400 (보낸 쪽이 고쳐야 하는 문제)
    if (Object.keys(errors).length > 0) {
      return badRequest(errors);
    }

    // 4) 모두 통과 → 접수 번호를 만들어요. (설계서 ③ 처리 중 일부)
    //    ※ 바이어 연결과 DB 저장(설계서 ③·④)은 다음 섹션에서 붙여요.
    const receiptNo = makeReceiptNo();

    // 5) 201 = "새로 하나 만들어졌어요(접수됐어요)"라는 뜻의 성공 번호예요. (설계서 ⑤ 응답)
    return Response.json(
      {
        message: "견적 요청이 접수되었어요. 영업일 기준 1~2일 안에 이메일로 견적을 보내 드릴게요.",
        receiptNo,
        receivedAt: new Date().toISOString(), // 설계서 '기록': 접수 시각
      },
      { status: 201 },
    );
  } catch (error) {
    // 6) 예상하지 못한 문제(서버 쪽 문제) → 500
    //    자세한 에러 내용은 서버 기록(터미널)에만 남기고, 화면에는 보여 주지 않아요. (설계서 ⑥)
    console.error("[견적 요청 접수] 서버 오류:", error);
    return Response.json({ message: "잠시 후 다시 시도해 주세요." }, { status: 500 });
  }
}

// ─────────────────────────────────────────────────────────────
// 아래는 위에서 쓰는 작은 도우미 함수들이에요.
// ─────────────────────────────────────────────────────────────

// 400 응답 만들기: 대표 메시지 하나 + 칸별 안내 목록을 함께 돌려줘요.
function badRequest(errors: Record<string, string>) {
  return Response.json(
    {
      message: Object.values(errors)[0], // 화면 위쪽에 크게 보여 줄 첫 번째 안내
      errors, // 칸 옆에 하나씩 보여 줄 안내들 (예: { email: "이메일 주소를 확인해 주세요." })
    },
    { status: 400 },
  );
}

// 글자 칸 정리: 글자가 아니면 빈 글자로, 글자면 앞뒤 빈칸을 잘라 내요.
function text(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

// 숫자 칸 정리: 숫자나 "500" 같은 숫자 글자를 숫자로 바꿔요.
// 비어 있으면 undefined(= 입력 안 함), 숫자로 못 바꾸면 NaN(= 이상한 값)을 돌려줘요.
function toNumber(value: unknown): number | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    if (value.trim() === "") return undefined;
    return Number(value);
  }
  return NaN; // 숫자도 글자도 아닌 것(예: 목록, true/false)은 이상한 값으로 처리
}

// "2026-12-31" 모양이고, 실제로 있는 날짜인지 확인해요. (2026-02-30 같은 날짜는 걸러요)
function isValidDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

// 오늘 날짜를 "2026-11-16" 모양으로 만들어요. (한국 시간 기준)
function todayString(): string {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Seoul" }).format(new Date());
}

// 접수 번호 만들기: "Q-날짜-무작위4자리" 모양 (예: Q-20261116-4821)
// ※ 지금은 무작위라 아주 드물게 겹칠 수 있어요. DB를 붙이면 DB가 겹치지 않는 번호를 만들어 줘요.
function makeReceiptNo(): string {
  const date = todayString().replaceAll("-", "");
  const random = Math.floor(1000 + Math.random() * 9000);
  return `Q-${date}-${random}`;
}
