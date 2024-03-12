import { AskRequest, AskResponse, ChatRequest } from "./models";


export async function askApi(options: AskRequest): Promise<AskResponse> {
    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: options.question,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory,
                vector_ranker: options.overrides?.vectorRanker, //:vik: added vector_ranker
            }
        })
    });


    if (!response.ok) {
        const data = await response.json();
        if (data.error === 'login_required') {
            window.location.href = data.login_url;
        }
        throw new Error("User is not logged in");
    }


    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }


    return parsedResponse;
}


export async function chatApi(options: ChatRequest): Promise<AskResponse> {
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "chatComponent"
        },
        body: JSON.stringify({
            history: options.history,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory,
                suggest_followup_questions: options.overrides?.suggestFollowupQuestions,
                vector_ranker: options.overrides?.vectorRanker, //:vik: added vector_ranker
            }
        })
    });


    if (response.status === 403) {
        const data = await response.json();
        // if (data.error === 'login_required') {
        //     window.location.href = data.login_url;
        // }
        throw new Error("login_required");
    }


    if (!response.ok) {
        const data = await response.json();
        if (data.error === 'login_required') {
            window.location.href = data.login_url;
        }
        throw new Error("User is not logged in");
    }


    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }


    return parsedResponse;
}


//:vik: api request for getting selected session data
export async function fetchChatSession(sessionId: string): Promise<any> {  // Replace any with the actual type of the response
    const response = await fetch(`/chatSession/${sessionId}`, {
        method: "GET",  // Assuming it's a GET request
        headers: {
            "Content-Type": "application/json"
        },
    });


    if (!response.ok) {
        const data = await response.json();
        if (data.error === 'login_required') {
            window.location.href = data.login_url;
        }
        throw new Error("Failed to fetch chat session");
    }


    const parsedResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }


    return parsedResponse;
}


export function getCitationFilePath(citation: string): string {
    return `/content/${citation}`;
}



