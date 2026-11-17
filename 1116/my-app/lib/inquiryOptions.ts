// 견적 요청에서 "목록에서 고르는" 값들을 한곳에 모아 둔 파일이에요.
// 화면(폼)과 서버(API 검사)가 둘 다 이 파일을 읽기 때문에,
// 여기만 고치면 두 곳이 항상 똑같은 목록을 쓰게 돼요.

export const COUNTRIES = ["대한민국", "미국", "일본", "중국", "베트남", "독일"];
export const PRODUCTS = ["(가상) 샘플 상품 A", "(가상) 샘플 상품 B", "(가상) 샘플 상품 C"];
export const TRADE_TERMS = ["FOB", "CIF", "EXW"];

// 요청사항(메시지) 최대 글자 수 (설계서 ①: 1000자 이하)
export const MAX_MESSAGE_LENGTH = 1000;
