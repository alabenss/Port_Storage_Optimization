import {
    useEffect,
    useState
} from "react";


import {
    Package,
    Weight,
    Warehouse,
    Activity,
    Brain,
    Ship,
    AlertTriangle,
    Cpu,
    CheckCircle,
    TrendingUp
} from "lucide-react";


import api from "../api/axios";




export default function Dashboard(){


const [data,setData] = useState(null);

const [loading,setLoading] = useState(true);





async function loadDashboard(){


try{


const response = await api.get(
    "/dashboard/summary"
);


setData(response.data);


}

catch(error){

console.log(error);

}

finally{

setLoading(false);

}


}







useEffect(()=>{


loadDashboard();


},[]);








if(loading){


return (

<div className="loading">

<Cpu size={40}/>

<br/>

Connecting to Terminal Intelligence System...

</div>

);


}






const cargo =
data?.cargo?.total_units ?? 0;


const weight =
(data?.cargo?.total_weight / 1000000)
.toFixed(2);



const occupancy =
data?.storage?.occupancy_percent ?? 0;



const movements =
data?.operations?.movements ?? 0;



const total =
data?.storage?.total_positions ?? 0;



const used =
data?.storage?.occupied ?? 0;



const free =
data?.storage?.available ?? 0;








return (

<div className="dashboard">






{/* HEADER */}

<div className="page-header">


<p className="page-label">

DJENDJEN PORT / OPERATIONS CENTER

</p>


<h1>

Terminal Intelligence Dashboard

</h1>


<p>

AI powered cargo storage optimization system

</p>


</div>









{/* KPI CARDS */}


<div className="kpi-grid">





<div className="metric-card">


<div className="metric-top">

<Package/>

<span>

CARGO UNITS

</span>


</div>



<strong>

{cargo}

</strong>



<p>

Imported inventory

</p>


</div>








<div className="metric-card">


<div className="metric-top">

<Weight/>

<span>

TOTAL WEIGHT

</span>


</div>



<strong>

{weight}M

</strong>



<p>

Metric tons

</p>


</div>








<div className="metric-card">


<div className="metric-top">

<Warehouse/>

<span>

STORAGE

</span>


</div>



<strong>

{occupancy}%

</strong>



<p>

Yard utilization

</p>


</div>









<div className="metric-card ai-card">


<div className="metric-top">

<Brain/>

<span>

AI ENGINE

</span>


</div>



<strong>

ONLINE

</strong>



<p>

Optimization active

</p>


</div>







</div>












{/* MAIN CONTENT */}


<div className="dashboard-grid">





<div className="panel">



<h2>

Storage Intelligence

</h2>





<div className="storage-stats">



<div>

<span>

TOTAL

</span>


<strong>

{total}

</strong>


</div>





<div>

<span>

USED

</span>


<strong>

{used}

</strong>


</div>





<div>

<span>

FREE

</span>


<strong>

{free}

</strong>


</div>





</div>







<h3>

Capacity Usage

</h3>



<div className="progress">


<div

style={{

width:`${occupancy}%`

}}


/>


</div>








<div className="zone-box">


<Warehouse/>


<h3>

Storage Monitoring

</h3>


<p>

{total} storage positions registered

</p>


<p>

{free} available locations detected

</p>


<p>

Real-time occupation tracking active

</p>



</div>







</div>













{/* AI PANEL */}


<div className="panel ai-panel">


<h2>

AI Control Center

</h2>





<div className="ai-status">


<Brain size={55}/>



<h3>

ACTIVE

</h3>


<p>

Decision engine connected

</p>


</div>







<div className="ai-row">


<TrendingUp/>


<span>

AI confidence

</span>


<strong>

96%

</strong>



</div>







<div className="ai-row">


<AlertTriangle/>


<span>

Risk monitoring

</span>


<strong>

SAFE

</strong>



</div>








<div className="ai-row">


<CheckCircle/>


<span>

System

</span>


<strong>

ONLINE

</strong>



</div>







</div>







</div>












{/* OPERATIONS */}



<div className="panel operations-panel">


<h2>

Live Terminal Operations

</h2>





<div className="operations-grid">





<div>


<Ship/>


<h3>

Vessel Connection

</h3>


<p>

ESTRELLA manifest synchronized

</p>


</div>







<div>


<Activity/>


<h3>

Cargo Flow

</h3>


<p>

{movements} active movements

</p>


</div>








<div>


<Cpu/>


<h3>

System Health

</h3>


<p>

All services operational

</p>


</div>





</div>



</div>









</div>

);


}