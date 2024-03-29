import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NDBI040 RavenDB example app",
  description: "RavenDB example app for NDBI040 by Lukáš Polák",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning={true}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
