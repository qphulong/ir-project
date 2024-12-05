import { Outlet } from "react-router-dom";
import { Flowbite } from "flowbite-react";
import { SimpleHeader } from "./SimpleHeader";
import { customTheme } from "../theme";
import { ToastContainer, Bounce } from "react-toastify";

interface SimpleLayoutProps {
    header?: boolean;
    className?: string;
}

export function SimpleLayout(props: SimpleLayoutProps) {
    return (
        <Flowbite theme={{theme: customTheme}}>
            <div className={'min-h-screen flex flex-col antialiased' + (props.className ? ' ' + props.className : '')}>
                {(props.header !== false) && <SimpleHeader />}
                <div className='my-auto'>
                    <Outlet />
                </div>
            </div>
            <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss={false}
                draggable
                pauseOnHover={false}
                theme="light"
                transition={Bounce}
            />
        </Flowbite>
    );
}