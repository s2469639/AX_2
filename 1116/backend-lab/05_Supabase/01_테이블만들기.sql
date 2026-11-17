-- (가상) 무역 문의 관리 — 연습용 테이블 3개
-- Supabase → SQL Editor → New query → 붙여 넣기 → Run

create table buyers (
  id bigint primary key generated always as identity,   -- 바이어 번호 (자동)
  company text not null,                                -- 회사명 (필수)
  country text not null,                                -- 국가 (필수)
  email text not null unique,                           -- 이메일 (필수, 중복 금지)
  created_at timestamptz default now()
);

create table products (
  id bigint primary key generated always as identity,
  name text not null unique,
  unit_price_usd numeric not null check (unit_price_usd > 0),  -- 단가는 0보다 커야
  stock integer not null default 0 check (stock >= 0)          -- 재고는 음수 금지
);

create table inquiries (
  id bigint primary key generated always as identity,
  buyer_id bigint not null references buyers(id),       -- 어느 바이어의 문의? (관계)
  product_id bigint not null references products(id),   -- 어느 상품? (관계)
  quantity integer not null check (quantity > 0),
  status text not null default '신규' check (status in ('신규','견적발송','계약','보류')),
  created_at timestamptz default now()
);

-- 보안: 세 표 모두 RLS(출입 통제) 켜기
alter table buyers enable row level security;
alter table products enable row level security;
alter table inquiries enable row level security;
