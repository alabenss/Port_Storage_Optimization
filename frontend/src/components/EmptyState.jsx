import {
Database
} from "lucide-react";


export default function EmptyState({
message
}){


return (

<div className="
bg-slate-900
rounded-xl
p-10
text-center
">


<Database
className="
mx-auto
text-slate-500
mb-4
"
/>


<h3 className="
text-slate-400
">

{message}

</h3>


</div>

)


}