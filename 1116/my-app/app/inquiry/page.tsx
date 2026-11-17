// "use client" = 이 화면은 브라우저 안에서 움직여요.
// (버튼 클릭, 입력값 기억, 서버에 보내기 같은 "반응"이 필요하면 꼭 써야 해요)
"use client";

import { useRef, useState, type FormEvent } from "react";
import { COUNTRIES, MAX_MESSAGE_LENGTH, PRODUCTS } from "@/lib/inquiryOptions";

// 서버가 돌려주는 답의 모양 (route.ts 의 POST 가 이 모양으로 보내요)
type ServerReply = {
  message: string; // 화면에 보여 줄 대표 문구
  receiptNo?: string; // 성공(201)일 때만 있는 접수 번호
  errors?: Record<string, string>; // 실패(400)일 때 칸별 안내
};

// 폼 아래에 보여 줄 결과 상자의 상태
type Result =
  | { kind: "success"; message: string; receiptNo?: string }
  | { kind: "error"; message: string };

export default function InquiryPage() {
  // 지금 서버에 보내는 중인지 (true 면 버튼을 잠가요)
  const [submitting, setSubmitting] = useState(false);
  // 폼 아래 결과 상자에 보여 줄 내용
  const [result, setResult] = useState<Result | null>(null);
  // 칸 옆에 빨갛게 보여 줄 안내들 (예: { email: "이메일을 입력해 주세요." })
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  // 두 번 누름 방지용 "잠금 표시". 화면이 다시 그려지기 전의 아주 빠른 두 번째 클릭까지 막아요.
  const lockRef = useRef(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    // 기본 동작(페이지 새로고침)을 막고, 우리가 직접 서버에 보내요.
    event.preventDefault();
    if (lockRef.current) return; // 이미 보내는 중이면 무시
    lockRef.current = true;
    setSubmitting(true);
    setResult(null);
    setFieldErrors({});

    const form = event.currentTarget;
    const formData = new FormData(form);

    // 폼에 적힌 값을 서버가 기대하는 모양(JSON)으로 묶어요.
    const payload = {
      company: formData.get("company"),
      email: formData.get("email"),
      country: formData.get("country"),
      product: formData.get("product"),
      quantity: formData.get("quantity"),
      message: formData.get("message"),
    };

    try {
      const response = await fetch("/api/inquiries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const reply = (await response.json()) as ServerReply;

      if (response.ok) {
        // 201: 접수 성공 → 성공 문구 + 접수 번호 보여 주고, 폼은 비워요.
        setResult({ kind: "success", message: reply.message, receiptNo: reply.receiptNo });
        form.reset();
      } else {
        // 400 / 500: 서버가 보내 준 친절한 문구를 그대로 보여 줘요.
        setResult({ kind: "error", message: reply.message ?? "잠시 후 다시 시도해 주세요." });
        setFieldErrors(reply.errors ?? {});
      }
    } catch {
      // 인터넷이 끊겼거나 서버가 꺼져서 답 자체를 못 받은 경우
      setResult({ kind: "error", message: "잠시 후 다시 시도해 주세요." });
    } finally {
      // 성공이든 실패든, 끝나면 버튼 잠금을 풀어요.
      lockRef.current = false;
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-lg">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">(가상) 바이어 문의</h1>
        <p className="mt-2 text-gray-500">
          아래 내용을 남겨 주시면 담당자가 확인 후 이메일로 연락드려요.{" "}
          <span className="text-red-600">*</span> 표시는 꼭 입력해 주세요.
        </p>

        {/* noValidate: 브라우저 자체 경고 대신, 서버가 보내 주는 친절한 안내를 쓰려고 꺼 뒀어요. */}
        <form
          onSubmit={handleSubmit}
          noValidate
          className="mt-8 space-y-5 rounded-2xl bg-white p-6 shadow-md sm:p-8"
        >
          <Field label="회사명" name="company" required error={fieldErrors.company}>
            <input
              id="company"
              name="company"
              type="text"
              autoComplete="organization"
              placeholder="(가상) 하늘상사"
              className={inputClass(fieldErrors.company)}
            />
          </Field>

          <Field label="이메일" name="email" required error={fieldErrors.email}>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="buyer@example.com"
              className={inputClass(fieldErrors.email)}
            />
          </Field>

          {/* 국가와 상품은 화면이 넓으면 나란히, 좁으면 위아래로 놓여요. */}
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="국가" name="country" required error={fieldErrors.country}>
              <select id="country" name="country" defaultValue="" className={inputClass(fieldErrors.country)}>
                <option value="" disabled>
                  선택해 주세요
                </option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="상품" name="product" required error={fieldErrors.product}>
              <select id="product" name="product" defaultValue="" className={inputClass(fieldErrors.product)}>
                <option value="" disabled>
                  선택해 주세요
                </option>
                {PRODUCTS.map((product) => (
                  <option key={product} value={product}>
                    {product}
                  </option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="수량" name="quantity" required error={fieldErrors.quantity}>
            <input
              id="quantity"
              name="quantity"
              type="number"
              inputMode="numeric"
              min={1}
              step={1}
              placeholder="500"
              className={inputClass(fieldErrors.quantity)}
            />
          </Field>

          <Field label="메시지" name="message" error={fieldErrors.message}>
            <textarea
              id="message"
              name="message"
              rows={4}
              maxLength={MAX_MESSAGE_LENGTH}
              placeholder="희망 납기, 포장 조건 등 궁금한 점을 적어 주세요. (선택)"
              className={inputClass(fieldErrors.message)}
            />
          </Field>

          {/* disabled={submitting}: 보내는 중에는 버튼이 눌리지 않아요. */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full cursor-pointer rounded-full bg-green-600 px-6 py-3 font-medium text-white shadow-md transition-colors hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {submitting ? "보내는 중…" : "문의 보내기"}
          </button>
        </form>

        {/* 서버 응답을 보여 주는 상자. aria-live 는 화면 읽기 프로그램이 새 문구를 읽어 주게 해요. */}
        <div aria-live="polite" className="mt-6">
          {result?.kind === "success" && (
            <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-green-800">
              <p className="font-medium">{result.message}</p>
              {result.receiptNo && (
                <p className="mt-1 text-sm">
                  접수 번호: <span className="font-mono font-semibold">{result.receiptNo}</span>
                </p>
              )}
            </div>
          )}
          {result?.kind === "error" && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 font-medium text-red-700">
              {result.message}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

// ── 칸 하나(이름표 + 입력 + 안내 문구)를 그리는 작은 부품 ──────────
function Field({
  label,
  name,
  required,
  error,
  children,
}: {
  label: string;
  name: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="ml-0.5 text-red-600">*</span>}
      </label>
      <div className="mt-1.5">{children}</div>
      {/* 서버가 이 칸에 대해 안내를 보냈으면 칸 바로 아래에 빨간 글씨로 보여 줘요. */}
      {error && <p className="mt-1.5 text-sm text-red-600">{error}</p>}
    </div>
  );
}

// 입력 칸 공통 모양. 안내(에러)가 있으면 테두리를 빨갛게 바꿔요.
function inputClass(error?: string) {
  return [
    "block w-full rounded-lg border bg-white px-3 py-2.5 text-gray-900 placeholder:text-gray-400",
    "focus:outline-none focus:ring-2",
    error ? "border-red-400 focus:ring-red-200" : "border-gray-300 focus:border-green-600 focus:ring-green-100",
  ].join(" ");
}
