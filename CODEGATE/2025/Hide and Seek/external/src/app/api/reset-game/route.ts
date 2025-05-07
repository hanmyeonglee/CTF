import { NextRequest, NextResponse } from "next/server";

const blockedIPs = new Set<string>();

export async function POST(req: NextRequest) {
    console.log(req.headers)
    const body = await req.json();

    const ip =
        req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
        "unknown";

    if (ip === "unknown") {
        return NextResponse.json({ error: "Unable to get client IP." }, { status: 400 });
    }

    if (blockedIPs.has(ip)) {
        return NextResponse.json({ error: "This IP cannot be used yet. Please Try again later." }, { status: 403 });
    }

    try {
        const response = await fetch(`${body.url}?date=${Date()}&message=Congratulation! you found button!`, {
            method: "GET",
            redirect: "manual",
        });

        if (!response.ok) {
            console.log(response);
            return NextResponse.json({ error: `Failed to fetch the URL. Status: ${response.status}` }, { status: 500 });
        }

        blockedIPs.add(ip);
        setTimeout(() => blockedIPs.delete(ip), 10 * 60 * 1000);

        console.log(`IP ${ip} Blocked`);

        return NextResponse.json({ message: "Sended!" }, { status: 200 });
    } catch (error) {
        if (error instanceof Error) {
            return NextResponse.json({ error: `An error occurred while fetching. Error message: ${error.message}` }, { status: 500 });
        } else {
            return NextResponse.json({ error: `An unexpected error occurred.` }, { status: 500 });
        }
    };


}