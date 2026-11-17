-- 상품 목록만 "누구나 읽기" 허용 (홈페이지에 보여 줄 용도)
-- 바이어 · 문의는 허용하지 않음 → 홈페이지에서 읽을 수 없음 (개인정보 보호)
grant select on public.products to anon;

create policy "누구나 상품 목록 읽기"
on public.products
for select to anon
using (true);
