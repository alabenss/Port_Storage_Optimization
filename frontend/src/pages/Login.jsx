import {
useState
} from "react";


import {
useNavigate
} from "react-router-dom";

import {
useAuth
} from "../context/AuthContext"; 


import api from "../api/axios";



export default function Login(){


const navigate=useNavigate();


const [username,setUsername]=useState("");

const [password,setPassword]=useState("");



async function submit(){


try{


const res =
await api.post(
"/auth/login",
null,
{
params:{
username,
password
}
}
);



const {
login
}=useAuth();


login(
res.data.user
);



navigate("/");


}catch(error){

alert(
"Login failed"
);

}



}




return (

<div className="
h-screen
flex
items-center
justify-center
bg-slate-950
">


<div className="
bg-slate-900
p-10
rounded-xl
w-[400px]
">


<h1 className="
text-3xl
font-bold
mb-8
text-center
">

PortAI

</h1>



<input

className="input"

placeholder="Username"

value={username}

onChange={
e=>setUsername(e.target.value)
}

/>



<input

className="input"

type="password"

placeholder="Password"

value={password}

onChange={
e=>setPassword(e.target.value)
}

/>



<button

onClick={submit}

className="
bg-cyan-500
text-black
font-bold
w-full
p-3
rounded-lg
mt-5
"

>

Login

</button>



</div>


</div>


)

}