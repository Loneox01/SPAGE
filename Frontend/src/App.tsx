import "./App.css";
import { useState } from "react";

interface BaseElement {
    id: string; // element unique id
    type: "text" | "image";
    z_index: number;
}

interface TextElement extends BaseElement {
    type: "text";
    content: string;
    color: string;
    font: string;
    font_size: string;  // int + px (i.e. "20px")
    x: string;  // int + % (i.e. "20%")
    y: string;
}

interface ImageElement extends BaseElement {
    type: "image";
    url: string;
    x: string;  // int + %
    y: string;
    width: string;  // int + px
}

type UIElement = TextElement | ImageElement

function App() {
    // entire UI state
    const [uiState, setUiState] = useState({
        prompt: "",
        bgColor: "rgb(34, 34, 34)",
        placeholder: "Enter an instruction",
        elements: [] as UIElement[]
    });
    const [isError, setIsError] = useState(false);

    const handlers: Record<string, (payload: any) => void> = {
        change_background: (payload) => {
            const { r, g, b } = payload;
            setUiState(prev => ({ ...prev, bgColor: `rgb(${r}, ${g}, ${b})` }));
        },

        spawn_text: (payload) => {
            setUiState(prev => ({
                ...prev,
                elements: [...prev.elements, { ...payload, type: "text" }] // assign type
            }));
        },
        edit_text: (payload) => {
            const exists = uiState.elements.some(el => el.id === payload.id);

            if (!exists) {
                // id not found
                setUiState(prev => ({
                    ...prev,
                    prompt: "",
                    placeholder: "Something went wrong... (ID not found)"
                }));

                triggerError();
                return;
            }

            setUiState(prev => ({
                ...prev,
                elements: prev.elements.map(el =>
                    el.id === payload.id ? { ...el, ...payload } : el
                )
            }));
        },
        spawn_image: (payload) => {
            setUiState(prev => ({
                ...prev,
                elements: [...prev.elements, { ...payload, type: "image" }]
            }));
        },
        edit_image: (payload) => {
            setUiState(prev => ({
                ...prev,
                elements: prev.elements.map(el =>
                    el.id === payload.id ? { ...el, ...payload } : el
                )
            }));
        },
        delete_elements: (payload) => {
            const { ids } = payload;

            setUiState(prev => ({
                ...prev,
                elements: prev.elements.filter(el => !ids.includes(el.id))
            }));
        },
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch("http://localhost:8000/prompt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                // send the entire UI to backend
                body: JSON.stringify({
                    text: uiState.prompt,
                    state: uiState
                }),
            });

            const data = await response.json();

            if (data.status === "success" && data.actions) {
                // Loop through every action the AI requested
                data.actions.forEach((toolResult: any) => {
                    const { action, payload } = toolResult;
                    if (action in handlers) {
                        handlers[action](payload);
                    }
                });
            }
            else {
                setUiState(prev => ({
                    ...prev,
                    prompt: "",
                    placeholder: `Unable to execute: ${data.error || "UNKNOWN_Error"}`
                }));
                triggerError();
                return;
            }

            setUiState(prev => ({
                ...prev,
                prompt: "",
                placeholder: "Enter an instruction"
            }));
        } catch (error) {
            setUiState(prev => ({
                ...prev,
                prompt: "",
                placeholder: "Something went wrong..."
            }));
            triggerError();
            return;
        }
    };

    const triggerError = () => {
        setIsError(true);
        setTimeout(() => setIsError(false), 500);
    };

    return (
        <div style={{
            height: "100vh",
            width: "100vw",
            backgroundColor: uiState.bgColor,
            position: "relative",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            transition: "all 0.8s ease",
            overflow: "hidden"
        }}>
            {uiState.elements.map((el) => (
                <div
                    key={el.id}
                    style={{
                        position: "absolute",
                        left: el.x,
                        top: el.y,
                        zIndex: el.z_index,
                        transition: "all 0.5s ease",
                        pointerEvents: "none",
                        transform: "translate(-50%, -50%)"  // ensures screen matches [0, 100]% request to AI
                    }}
                >
                    {/* Text element */}
                    {el.type === "text" && (
                        <div style={{
                            color: el.color || "white",  // default color white for invalid color
                            fontFamily: el.font ? `${el.font}, sans-serif` : "sans-serif",  // default font sans-serif for invalid font
                            fontSize: el.font_size,
                        }}>
                            {el.content}
                        </div>
                    )}
                    {/* Render logic for Images */}
                    {el.type === "image" && (
                        <img
                            src={el.url}
                            alt=""
                            style={{
                                width: el.width,
                                height: "auto",
                                borderRadius: "8px",
                                display: "block",
                                boxShadow: "0 4px 10px rgba(0,0,0,0.1)"
                            }}
                        />
                    )}
                </div>
            ))}

            {/* Command bar layer */}
            <form
                onSubmit={handleSubmit}
                style={{
                    zIndex: 101,
                    position: "absolute",
                    bottom: "40px",
                    left: "50%",
                    transform: "translateX(-50%)",
                    display: "flex",
                    gap: "10px"
                }}
            >
                <input
                    className={isError ? "error-shake" : ""}
                    value={uiState.prompt}
                    onChange={(e) => setUiState(prev => ({ ...prev, prompt: e.target.value }))}
                    placeholder={uiState.placeholder}
                    style={{
                        padding: "10px 12px",
                        width: "300px",
                        borderRadius: "6px",
                        border: "1px solid #ccc"
                    }}
                />
                <button type="submit">Send</button>
            </form>
        </div>
    );
}

export default App;