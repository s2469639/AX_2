export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-gray-50 px-6 text-center">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        (가상) 한빛무역 문의 센터
      </h1>
      <p className="max-w-md text-lg leading-relaxed text-gray-500">
        견적, 납기, 샘플 요청 등 궁금한 점을 남겨 주시면 담당자가 확인해 드려요.
      </p>
      <button
        type="button"
        className="cursor-pointer rounded-full bg-green-600 px-6 py-3 font-medium text-white shadow-md transition-colors hover:bg-green-700"
      >
        문의 시작하기
      </button>
    </main>
  );
}
