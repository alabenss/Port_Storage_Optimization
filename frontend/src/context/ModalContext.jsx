import {
    createContext,
    useContext,
    useState
} from "react";


const ModalContext = createContext();



export function ModalProvider({children}){


    const [modal,setModal] = useState(null);



    function showAlert(message){

    console.log("MODAL TEST:", message);

    setModal({

        type:"alert",
        message

    });


}



    function confirm(message){

        return new Promise((resolve)=>{


            setModal({

                type:"confirm",

                message,

                resolve

            });


        });

    }




    function close(result){


        if(modal?.resolve){

            modal.resolve(result);

        }


        setModal(null);

    }





    return (

        <ModalContext.Provider

        value={{
            showAlert,
            alert: showAlert,
            confirm
        }}

        >


            {children}



            {
            modal && (


            <div className="modal-overlay">


                <div className="modal">


                    <h2>

                    {
                    modal.type==="confirm"
                    ?
                    "Confirmation Required"
                    :
                    "Information"

                    }

                    </h2>



                    <p>

                    {modal.message}

                    </p>




                    <div className="modal-buttons">


                    {
                    modal.type==="confirm"
                    &&

                    <button

                    className="cancel-button"

                    onClick={()=>close(false)}

                    >

                    Cancel

                    </button>

                    }



                    <button

                    className={
                    modal.type==="confirm"
                    ?
                    "danger-button"
                    :
                    "primary-button"
                    }


                    onClick={()=>close(true)}

                    >

                    {
                    modal.type==="confirm"
                    ?
                    "Confirm"
                    :
                    "OK"

                    }


                    </button>


                    </div>



                </div>



            </div>


            )

            }



        </ModalContext.Provider>


    );


}




export function useModal(){

    return useContext(ModalContext);

}