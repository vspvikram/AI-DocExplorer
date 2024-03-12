import { Example } from "./Example";


import styles from "./Example.module.css";


export type ExampleModel = {
    text: string;
    value: string;
};


const EXAMPLES: ExampleModel[] = [
    {
        text: "What are single-photon sources and why are they important?",
        value: "What are single-photon sources and why are they important?"
    },
    {
        text: "How can quantum mechanics help us design better materials?",
        value: "How can quantum mechanics help us design better materials?"
    },
    { 
        text: "What are some applications of quantum phase estimation?",
        value: "What are some applications of quantum phase estimation?" 
    }
];


interface Props {
    onExampleClicked: (value: string) => void;
}


export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};



