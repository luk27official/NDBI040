import { ClientComp } from "./clientcomp";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <ClientComp />
    </main>
  );
}
