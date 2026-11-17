// ─────────────────────────────────────────────────────────────
// 상품 목록 화면  (주소: /products)
//
// Supabase 의 products 표를 읽어서 상품명 · 단가 · 재고를 카드로 보여 줘요.
// 이 화면은 "서버"에서 만들어져요. 그래서 데이터베이스를 읽는 코드가 브라우저로 새어 나가지 않아요.
// ─────────────────────────────────────────────────────────────

import { Suspense } from "react";
import { io } from "next/cache";
import { getSupabase } from "@/lib/supabase";

// products 표 한 줄의 모양 (05_Supabase/01_테이블만들기.sql 과 같은 칸 이름)
type Product = {
  id: number;
  name: string; // 상품명
  unit_price_usd: number; // 단가 (USD)
  stock: number; // 재고
};

export default function ProductsPage() {
  return (
    <main className="min-h-screen bg-gray-50 px-4 py-12">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">(가상) 상품 목록</h1>
        <p className="mt-2 text-gray-500">단가와 현재 재고를 확인할 수 있어요.</p>

        {/* Suspense: 데이터를 읽어 오는 동안 fallback(뼈대 카드)을 먼저 보여 주고,
            다 읽으면 진짜 카드로 바꿔 끼워요. */}
        <Suspense fallback={<ProductGridSkeleton />}>
          <ProductList />
        </Suspense>
      </div>
    </main>
  );
}

// ── 실제로 데이터베이스를 읽어서 카드를 그리는 부분 ──────────────
async function ProductList() {
  // io(): "여기부터는 방문할 때마다 새로 읽어요" 라는 표시.
  // (재고는 계속 바뀌니까, 미리 만들어 둔 옛날 화면을 보여 주면 안 돼요)
  await io();

  // 1) 연결 준비. .env.local 설정이 없으면 친절한 안내를 보여 줘요.
  const supabase = getSupabase();
  if (!supabase) {
    return (
      <Notice tone="warning" title="데이터베이스 연결 설정이 아직 없어요.">
        my-app 폴더의 .env.local 파일에 Supabase 주소와 공개 키를 넣은 뒤, 개발 서버를 다시 켜 주세요.
      </Notice>
    );
  }

  // 2) products 표에서 필요한 칸만, 상품명 순서로 읽어요.
  let products: Product[] = [];
  try {
    const { data, error } = await supabase
      .from("products")
      .select("id, name, unit_price_usd, stock")
      .order("name");

    if (error) throw error; // Supabase 가 "못 읽었어요" 라고 답한 경우
    products = data ?? [];
  } catch (error) {
    // 자세한 에러 내용은 서버 기록(터미널)에만 남기고, 화면에는 쉬운 말만 보여 줘요.
    console.error("[상품 목록] 불러오기 실패:", error);
    return (
      <Notice tone="error" title="상품 목록을 불러오지 못했어요.">
        잠시 후 새로고침해 주세요. 계속 안 되면 담당자에게 알려 주세요.
      </Notice>
    );
  }

  // 3) 표는 읽었는데 상품이 0개인 경우
  if (products.length === 0) {
    return (
      <Notice tone="info" title="아직 등록된 상품이 없어요.">
        Supabase 의 products 표에 상품을 추가하면 여기에 보여요.
      </Notice>
    );
  }

  // 4) 카드로 보여 주기. 화면이 넓으면 3줄, 중간이면 2줄, 좁으면 1줄로 놓여요.
  return (
    <ul className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </ul>
  );
}

// ── 상품 카드 한 장 ─────────────────────────────────────────
function ProductCard({ product }: { product: Product }) {
  const lowStock = product.stock <= 10; // 재고 10개 이하면 "부족" 표시
  return (
    <li className="flex flex-col rounded-2xl bg-white p-6 shadow-md">
      <h2 className="text-lg font-semibold text-gray-900">{product.name}</h2>

      <p className="mt-4 text-3xl font-bold text-gray-900">
        {formatUsd(product.unit_price_usd)}
        <span className="ml-1 text-sm font-normal text-gray-500">/ 개</span>
      </p>

      <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4 text-sm">
        <span className="text-gray-500">재고</span>
        <span
          className={`rounded-full px-2.5 py-0.5 font-medium ${
            lowStock ? "bg-amber-100 text-amber-800" : "bg-green-100 text-green-800"
          }`}
        >
          {product.stock.toLocaleString("ko-KR")}개{lowStock && " · 부족"}
        </span>
      </div>
    </li>
  );
}

// ── 읽어 오는 동안 보여 줄 회색 뼈대 카드 3장 ────────────────────
function ProductGridSkeleton() {
  return (
    <ul className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-label="상품 목록을 불러오는 중">
      {[0, 1, 2].map((i) => (
        <li key={i} className="h-44 animate-pulse rounded-2xl bg-white p-6 shadow-md">
          <div className="h-5 w-2/3 rounded bg-gray-200" />
          <div className="mt-5 h-8 w-1/3 rounded bg-gray-200" />
          <div className="mt-7 h-4 w-full rounded bg-gray-100" />
        </li>
      ))}
    </ul>
  );
}

// ── 안내 상자 (설정 없음 / 에러 / 비어 있음) ──────────────────────
function Notice({
  tone,
  title,
  children,
}: {
  tone: "info" | "warning" | "error";
  title: string;
  children: React.ReactNode;
}) {
  const colors = {
    info: "border-gray-200 bg-white text-gray-700",
    warning: "border-amber-200 bg-amber-50 text-amber-900",
    error: "border-red-200 bg-red-50 text-red-800",
  }[tone];
  return (
    <div role={tone === "error" ? "alert" : "status"} className={`mt-8 rounded-xl border p-5 ${colors}`}>
      <p className="font-semibold">{title}</p>
      <p className="mt-1 text-sm">{children}</p>
    </div>
  );
}

// 숫자를 "$12.00" 처럼 달러 모양으로 바꿔요.
function formatUsd(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}
