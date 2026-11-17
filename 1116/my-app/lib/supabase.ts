// ─────────────────────────────────────────────────────────────
// Supabase(데이터베이스)에 연결하는 코드
//
// 주소(URL)와 열쇠(KEY)는 코드에 직접 쓰지 않고 .env.local 파일에서 "이름으로" 꺼내 써요.
//   - NEXT_PUBLIC_SUPABASE_URL             : 내 Supabase 프로젝트 주소
//   - NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY : 공개용 열쇠 (누구나 봐도 되는 열쇠)
//
// 공개용 열쇠라도 마음대로 다 읽을 수 있는 건 아니에요.
// Supabase 의 출입 통제(RLS)가 허락한 것(지금은 products 읽기)만 할 수 있어요.
// ─────────────────────────────────────────────────────────────

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

// 한 번 만든 연결은 기억해 두고 다시 써요. (매번 새로 만들 필요 없음)
let client: SupabaseClient | null = null;

// 연결을 돌려줘요.
// .env.local 에 두 값 중 하나라도 없으면 null(= 연결 못 함)을 돌려줘서,
// 화면이 고장 나는 대신 "설정이 필요해요" 안내를 보여 줄 수 있게 해요.
export function getSupabase(): SupabaseClient | null {
  if (client) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !key) return null;

  client = createClient(url, key);
  return client;
}
