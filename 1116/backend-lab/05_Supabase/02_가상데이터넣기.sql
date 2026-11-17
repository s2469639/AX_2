-- 모두 (가상) 연습 데이터예요. 실제 회사 · 고객 정보를 넣지 마세요.
-- 두 번 Run 해도 괜찮게 만들었어요 (이미 있으면 건너뜀).

insert into buyers (company, country, email) values
  ('(가상) Sunrise Trading', '베트남', 'kim@sunrise.example'),
  ('(가상) Nordic Home', '스웨덴', 'anna@nordic.example')
on conflict (email) do nothing;

insert into products (name, unit_price_usd, stock) values
  ('샘플 상품 A', 12, 3000),
  ('샘플 상품 B', 30, 500),
  ('샘플 상품 C', 8, 1)
on conflict (name) do nothing;

-- 문의: 번호(1, 2…)를 직접 쓰지 않고 "이메일 · 상품명"으로 찾아서 연결해요
-- (번호가 1부터 시작하지 않아도 실패하지 않게)
insert into inquiries (buyer_id, product_id, quantity, status)
select b.id, p.id, v.quantity, v.status
from (values
  ('kim@sunrise.example', '샘플 상품 A', 500,  '신규'),
  ('kim@sunrise.example', '샘플 상품 B', 100,  '견적발송'),
  ('anna@nordic.example', '샘플 상품 A', 1200, '신규'),
  ('anna@nordic.example', '샘플 상품 C', 2000, '계약')
) as v(email, product_name, quantity, status)
join buyers   b on b.email = v.email
join products p on p.name  = v.product_name
where (select count(*) from inquiries) = 0;   -- 문의 표가 비어 있을 때만 넣기

-- 확인: 아래 결과가 buyers 2 · products 3 · inquiries 4 이면 성공
select 'buyers' as 표, count(*) as 줄수 from buyers
union all select 'products', count(*) from products
union all select 'inquiries', count(*) from inquiries;
