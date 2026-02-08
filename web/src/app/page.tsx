export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-stone-50 font-sans dark:bg-stone-950">
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col items-center justify-center gap-10 px-6 py-20">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-stone-900 dark:text-stone-100 sm:text-4xl">
            NotebookLM Transformer
          </h1>
          <p className="mt-3 text-lg text-stone-600 dark:text-stone-400">
            PDFスライドを編集可能なPowerPointに変換
          </p>
        </header>

        <section className="w-full rounded-2xl border border-stone-200 bg-white p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900">
          <p className="text-center text-stone-600 dark:text-stone-400">
            変換はCLIから実行できます。
          </p>
          <pre className="mt-4 overflow-x-auto rounded-lg bg-stone-100 p-4 text-sm dark:bg-stone-800">
            <code>
              {`# プロジェクトルートで
python -m src.main input/slide.pdf -o output/result.pptx`}
            </code>
          </pre>
        </section>

        <footer className="text-center text-sm text-stone-500 dark:text-stone-500">
          <a
            href="https://nextjs.org/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-stone-700 dark:hover:text-stone-300"
          >
            Next.js Documentation
          </a>
        </footer>
      </main>
    </div>
  );
}
