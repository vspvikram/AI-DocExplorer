import { useRef, useState, useEffect, useCallback } from "react";
import { Checkbox, Panel, DefaultButton, TextField, SpinButton } from "@fluentui/react";
import { SparkleFilled } from "@fluentui/react-icons";


import styles from "./Chat.module.css";


import { chatApi, Approaches, AskResponse, ChatRequest, ChatTurn, fetchChatSession } from "../../api";
import { Answer, AnswerError, AnswerLoading } from "../../components/Answer";
import { QuestionInput } from "../../components/QuestionInput";
import { ExampleList } from "../../components/Example";
import { UserChatMessage } from "../../components/UserChatMessage";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import { SettingsButton } from "../../components/SettingsButton";
import { ClearChatButton } from "../../components/ClearChatButton";
import { ChatSession } from "../../components/ChatHistoryPanel/ChatHistoryPanel"; // Vik: adding chat history panel
import ChatHistoryPanel from "../../components/ChatHistoryPanel/ChatHistoryPanel";
import { useParams, useNavigate } from 'react-router-dom'; // Vik: adding useParams to get the session ID from the route


const Chat = () => {


    const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
    const [promptTemplate, setPromptTemplate] = useState<string>("");
    const [retrieveCount, setRetrieveCount] = useState<number>(5);
    const [useSemanticRanker, setUseSemanticRanker] = useState<boolean>(true);
    const [useVectorRanker, setUseVectorRanker] = useState<boolean>(true); // Vik: adding vector ranker checkbox
    const [useSemanticCaptions, setUseSemanticCaptions] = useState<boolean>(false);
    const [excludeCategory, setExcludeCategory] = useState<string>("");
    const [useSuggestFollowupQuestions, setUseSuggestFollowupQuestions] = useState<boolean>(false);


    const lastQuestionRef = useRef<string>("");
    const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);


    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<unknown>();


    const [activeCitation, setActiveCitation] = useState<string>();
    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);


    const [selectedAnswer, setSelectedAnswer] = useState<number>(0);
    const [answers, setAnswers] = useState<[user: string, response: AskResponse][]>([]);


    // Vik: adding const to set question box to disabled after chat limit is reached
    const [isQuestionDisabled, setIsQuestionDisabled] = useState<boolean>(false);


    // Vik: adding state to show chat history panel
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    // const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);  // Assuming ChatSession is the correct type for a chat session


    // const fetchChatSessions = async () => {
    //     try {
    //         const response = await fetch('/getChatHistory');  // Adjust the URL accordingly
    //         if (!response.ok) {
    //             throw new Error('Failed to fetch chat sessions');
    //         }
    //         const data = await response.json();
    //         setChatSessions(data);
    //     } catch (error) {
    //         console.error('Error fetching chat sessions:', error);
    //         // handle error accordingly
    //     }
    // };


    const handleSessionClick = useCallback(async (sessionId: string) => {
        error && setError(undefined);
        setIsLoading(true);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);
        
        try {


            const sessionData = await fetchChatSession(sessionId);
            // const formattedData = sessionData.chatData.map((turn: any) => ([turn.user, turn.bot]));
            const formattedData = sessionData.chatData.map((turn: any, index: number) => ([
                turn.user,
                {
                    answer: turn.bot,
                    thoughts: null,  // Assuming there are no thoughts data in the chatData
                    data_points: [],  // Assuming there are no data points in the chatData
                    Chat_Limit: 15,  // Placeholder value, replace with actual data if available
                    Current_Chat_Length:  index + 1 // sessionData.chatData.length
                }
            ]));


            lastQuestionRef.current = formattedData[formattedData.length - 1][0];
            setAnswers(formattedData);
            
            setCurrentSessionId(sessionData.id);
            console.log(formattedData);
            navigate(`/chatSession/${sessionId}`);  // Navigate to the new URL


            if (formattedData[formattedData.length - 1][1]?.Current_Chat_Length !== undefined && formattedData[formattedData.length - 1][1]?.Chat_Limit !== undefined) {
                setIsQuestionDisabled(formattedData[formattedData.length - 1][1].Current_Chat_Length >= formattedData[formattedData.length - 1][1].Chat_Limit)
            }
            // setIsLoading(false);
        } catch (error) {
            console.error('Error fetching chat session:', error);
            // handle error accordingly
        } finally {
            setIsLoading(false);
        }
    }, [navigate]);


    useEffect(() => {
        console.log(answers);  // This will log the new state after setAnswers is called and the component re-renders
    }, [answers]);


    // const onSessionSelected = (sessionId: string) => {
    //     // code to handle session selection
    //     handleSessionClick(sessionId);  // Assumes loadChatHistory is a function in your Chat component that loads the chat history for the selected session
    // };


    // useEffect(() => {
    //     fetchChatSessions();
    // }, []);  // Empty dependency array means this useEffect runs once



    const makeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;


        error && setError(undefined);
        setIsLoading(true);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);


        try {
            const history: ChatTurn[] = answers.map(a => ({ user: a[0], bot: a[1].answer }));
            const request: ChatRequest = {
                history: [...history, { user: question, bot: undefined }],
                approach: Approaches.ReadRetrieveRead,
                overrides: {
                    promptTemplate: promptTemplate.length === 0 ? undefined : promptTemplate,
                    excludeCategory: excludeCategory.length === 0 ? undefined : excludeCategory,
                    top: retrieveCount,
                    semanticRanker: useSemanticRanker,
                    vectorRanker: useVectorRanker, // Vik: adding vector ranker checkbox
                    semanticCaptions: useSemanticCaptions,
                    suggestFollowupQuestions: useSuggestFollowupQuestions
                }
            };
            const result = await chatApi(request);
            setAnswers([...answers, [question, result]]);


            // Vik: extracting and setting chat limit and current chat length
            if (result?.Current_Chat_Length !== undefined && result?.Chat_Limit !== undefined) {
                setIsQuestionDisabled(result.Current_Chat_Length >= result.Chat_Limit)
            }
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    };


    const clearChat = async () => {
        lastQuestionRef.current = "";
        error && setError(undefined);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);
        setAnswers([]);
        setIsQuestionDisabled(false);


        // Vik: adding code to make a request to server to reset chat session
        try {
            const response = await fetch('/clear_history', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });


            // if the response is not ok, throw an error
            if (!response.ok) {
                console.error("Failed to clear chat history on the server");
            }
        } catch (e) {
            // handle any exceptions that occur while making the request
            console.error("An error occurred while clearing chat history:", e);
        }
    };


    useEffect(() => chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" }), [isLoading]);


    const onPromptTemplateChange = (_ev?: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        setPromptTemplate(newValue || "");
    };


    const onRetrieveCountChange = (_ev?: React.SyntheticEvent<HTMLElement, Event>, newValue?: string) => {
        setRetrieveCount(parseInt(newValue || "3"));
    };


    const onUseSemanticRankerChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSemanticRanker(!!checked);
    };


    const onUseVectorRankerChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseVectorRanker(!!checked);
    }


    const onUseSemanticCaptionsChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSemanticCaptions(!!checked);
    };


    const onExcludeCategoryChanged = (_ev?: React.FormEvent, newValue?: string) => {
        setExcludeCategory(newValue || "");
    };


    const onUseSuggestFollowupQuestionsChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSuggestFollowupQuestions(!!checked);
    };


    const onExampleClicked = (example: string) => {
        makeApiRequest(example);
    };


    const onShowCitation = (citation: string, index: number) => {
        if (activeCitation === citation && activeAnalysisPanelTab === AnalysisPanelTabs.CitationTab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveCitation(citation);
            setActiveAnalysisPanelTab(AnalysisPanelTabs.CitationTab);
        }


        setSelectedAnswer(index);
    };


    const onToggleTab = (tab: AnalysisPanelTabs, index: number) => {
        if (activeAnalysisPanelTab === tab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveAnalysisPanelTab(tab);
        }


        setSelectedAnswer(index);
    };
    
    return (
        <div className={styles.mainContainer}>
            {/* Left container for ChatHistoryPanel */}
            <div className={styles.leftContainer}>
                <ChatHistoryPanel handleSessionClick={handleSessionClick}/>
            </div>
            <div className={styles.rightContainer}>
                <div className={styles.commandsContainer}>
                        <ClearChatButton className={styles.commandButton} onClick={clearChat} disabled={!lastQuestionRef.current || isLoading} />
                        <SettingsButton className={styles.commandButton} onClick={() => setIsConfigPanelOpen(!isConfigPanelOpen)} />
                </div>
                <div className={styles.chatRoot}>
                    <div className={styles.chatContainer}>
                        {!lastQuestionRef.current ? (
                            <div className={styles.chatEmptyState}>
                                {/* <SparkleFilled fontSize={"120px"} primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Chat logo" /> */}
                                <SparkleFilled fontSize={"120px"} primaryFill={"rgba(0, 102, 178, 1)"} aria-hidden="true" aria-label="Chat logo" />
                                <h1 className={styles.chatEmptyStateTitle}>Ask a question about quantum physics</h1>
                                <h2 className={styles.chatEmptyStateSubtitle}>Ask anything or try an example</h2>
                                <h3 className={styles.chatEmptyStateDisclaimer}><strong><u>DISCLAIMER:</u></strong> This is a beta product currently in testing phase. We value your feedback on the responses generated by QASA and encourage you to share your thoughts and suggestions. All chat sessions will be recorded for further development of the application.</h3>
                                <ExampleList onExampleClicked={onExampleClicked} />
                            </div>
                        ) : (
                            <div className={styles.chatMessageStream}>
                                {answers.map((answer, index) => (
                                    <div key={index}>
                                        <UserChatMessage message={answer[0]} />
                                        <div className={styles.chatMessageGpt}>
                                            <Answer
                                                key={index}
                                                answer={answer[1]}
                                                isSelected={selectedAnswer === index && activeAnalysisPanelTab !== undefined}
                                                onCitationClicked={c => onShowCitation(c, index)}
                                                onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab, index)}
                                                onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab, index)}
                                                onFollowupQuestionClicked={q => makeApiRequest(q)}
                                                showFollowupQuestions={useSuggestFollowupQuestions && answers.length - 1 === index}
                                            />
                                        </div>
                                    </div>
                                ))}
                                {/* setIsQuestionDisabled({answers[answers.length - 1][1].Current_Chat_Length > answers[answers.length - 1][1].Chat_Limit}) */}
                                {isLoading && (
                                    <>
                                        <UserChatMessage message={lastQuestionRef.current} />
                                        <div className={styles.chatMessageGptMinWidth}>
                                            <AnswerLoading />
                                        </div>
                                    </>
                                )}
                                {error ? (
                                    <>
                                        <UserChatMessage message={lastQuestionRef.current} />
                                        <div className={styles.chatMessageGptMinWidth}>
                                            <AnswerError 
                                                error={error.toString()} 
                                                onRetry={() => makeApiRequest(lastQuestionRef.current)}
                                            />
                                        </div>
                                    </>
                                ) : null}
                                <div ref={chatMessageStreamEnd} />
                            </div>
                        )}


                        <div className={styles.chatInput}>
                            <a 
                                href="https://forms.office.com/r/fvz69D8qAH" 
                                target="_blank" 
                                className={styles.feedbackLink}  /* Apply the new class here */
                            >
                                Click here to fill out the feedback form
                            </a>
                            <div className={isQuestionDisabled ? styles.disabledInput : styles.chatInput}>
                                <QuestionInput
                                    clearOnSend
                                    placeholder={ isQuestionDisabled ? "You reached the chat limit. Please click on \"Clear Chat\" button to start a new chat." : "Type a new question (e.g. Is entanglement necessary for all quantum computations?)"}
                                    disabled={ isLoading || isQuestionDisabled}
                                    onSend={question => makeApiRequest(question)}
                                />
                                {/* Show the disabled message when the input is disabled */}
                                {/* {isQuestionDisabled && (
                                    <div className={styles.disabledMessage}>Question input is currently disabled.</div>
                                )} */}
                            </div>
                        </div>
                    </div>


                    {answers.length > 0 && activeAnalysisPanelTab && (
                        <AnalysisPanel
                            className={styles.chatAnalysisPanel}
                            activeCitation={activeCitation}
                            onActiveTabChanged={x => onToggleTab(x, selectedAnswer)}
                            citationHeight="810px"
                            answer={answers[selectedAnswer][1]}
                            activeTab={activeAnalysisPanelTab}
                        />
                    )}


                    <Panel
                        headerText="Configure answer generation"
                        isOpen={isConfigPanelOpen}
                        isBlocking={false}
                        onDismiss={() => setIsConfigPanelOpen(false)}
                        closeButtonAriaLabel="Close"
                        onRenderFooterContent={() => <DefaultButton onClick={() => setIsConfigPanelOpen(false)}>Close</DefaultButton>}
                        isFooterAtBottom={true}
                    >
                        <TextField
                            className={styles.chatSettingsSeparator}
                            defaultValue={promptTemplate}
                            label="Override prompt template"
                            multiline
                            autoAdjustHeight
                            onChange={onPromptTemplateChange}
                        />


                        <SpinButton
                            className={styles.chatSettingsSeparator}
                            label="Retrieve this many documents from search:"
                            min={1}
                            max={50}
                            defaultValue={retrieveCount.toString()}
                            onChange={onRetrieveCountChange}
                        />
                        <TextField className={styles.chatSettingsSeparator} label="Exclude category" onChange={onExcludeCategoryChanged} />
                        <Checkbox
                            className={styles.chatSettingsSeparator}
                            checked={useSemanticRanker}
                            label="Use semantic ranker for retrieval"
                            onChange={onUseSemanticRankerChange}
                        />
                        <Checkbox
                            className={styles.chatSettingsSeparator}
                            checked={useVectorRanker}
                            label="Use vector ranker for retrieval"
                            onChange={onUseVectorRankerChange}
                        />
                        <Checkbox
                            className={styles.chatSettingsSeparator}
                            checked={useSemanticCaptions}
                            label="Use query-contextual summaries instead of whole documents"
                            onChange={onUseSemanticCaptionsChange}
                            disabled={!useSemanticRanker}
                        />
                        <Checkbox
                            className={styles.chatSettingsSeparator}
                            checked={useSuggestFollowupQuestions}
                            label="Suggest follow-up questions"
                            onChange={onUseSuggestFollowupQuestionsChange}
                        />
                    </Panel>
                </div> 
            </div>
        </div>
    );
};


export default Chat;



