import {
    useEffect,
    useState
} from "react";


import {
    Brain,
    CheckCircle,
    Target,
    Move,
    Package,
    ShieldAlert,
    Sparkles
} from "lucide-react";


import aiApi from "../api/aiApi";



export default function AI(){


const [data,setData] = useState(null);

const [decisions,setDecisions] = useState([]);

const [recommendations,setRecommendations] = useState([]);



async function load(){


    try{


        const dashboard = await aiApi.dashboard();

        const history = await aiApi.decisions();


        setData(
            dashboard.data
        );


        // Use the complete AI decision objects returned by the dashboard endpoint
        // (cargo_reference, cargo_type, handling_method, ai_score, confidence, etc.)
        const aiDecisions =
            dashboard.data.recent_decisions || [];

        setDecisions(
            aiDecisions
        );

        setRecommendations(
            dashboard.data.pending_recommendations || []
        );


    }catch(error){

        console.log(error);

    }


}



useEffect(()=>{

    load();

},[]);





if(!data){

return (

<div className="loading">


<br/>

Loading AI Engine...

</div>

);

}





return (

<div className="dashboard ai-page">



{/* HEADER */}

<div className="page-header">



<h1>


AI Control Center

</h1>


<p>

Smart terminal optimization and autonomous storage intelligence

</p>


</div>






{/* KPI */}

<div className="kpi-grid">



<Metric

icon={<CheckCircle/>}

title="AI ENGINE"

value={data.ai_engine.status}

/>



<Metric

icon={<Target/>}

title="RECOMMENDATIONS"

value={data.ai_engine.recommendations}

/>



<Metric

icon={<Move/>}

title="RELOCATIONS"

value={data.relocations.successful}

/>



<Metric

icon={<Package/>}

title="MULTI POSITION"

value={data.allocation_strategy.multi_position}

/>



</div>







<div className="dashboard-grid">





{/* AI STATUS */}

<div className="panel">


<h2>


 Intelligence Overview

</h2>



<div className="storage-stats">


<div>

<span>

Decision Engine

</span>


<strong className="success-text">

READY

</strong>


</div>



<div>

<span>

Optimization

</span>


<strong>

AUTOMATIC

</strong>


</div>



<div>

<span>

System

</span>


<strong className="success-text">

ONLINE

</strong>


</div>


</div>



</div>







{/* RISK */}

<div className="panel">


<h2>

<ShieldAlert/>

 Risk Monitor

</h2>



<div className="ai-row">

<span>

HIGH

</span>


<strong className="danger-text">

{data.risk_analysis.HIGH}

</strong>


</div>



<div className="ai-row">

<span>

MEDIUM

</span>


<strong>

{data.risk_analysis.MEDIUM}

</strong>


</div>



<div className="ai-row">

<span>

LOW

</span>


<strong>

{data.risk_analysis.LOW}

</strong>


</div>



</div>



</div>









{/* DECISIONS */}


<div className="panel operations-panel">


<h2>

Recent AI Decisions

</h2>



<div className="cargo-table">


<table>


<thead>

<tr>

<th>Cargo Reference</th>
<th>Type / Category</th>
<th>Handling</th>
<th>Weight</th>
<th>Position / Score</th>
<th>Confidence</th>


</tr>

</thead>




<tbody>



{

decisions.length === 0 ?


<tr>

<td colSpan="6" className="loading-cell">

No AI decisions available

</td>

</tr>



:


decisions.slice(0,10).map((item,index)=>(


<tr key={index}>


<td>
<div className="cargo-reference">
<strong>{item.cargo_reference || item.cargo_id}</strong>
<span>{item.cargo_type || "MANIFEST"}</span>
</div>
</td>

<td>
<strong>{item.cargo_category || "GENERAL"}</strong>
<br/>
<span>{item.cargo_type || "STANDARD"}</span>
</td>

<td>
{item.handling_method || "STANDARD"}
</td>

<td>
{Number(item.weight || 0).toLocaleString()} kg
</td>

<td>
<span className="status-badge">
Position {item.position}
</span>
<br/>
<small>AI Score: {item.ai_score ?? "N/A"}</small>
</td>

<td>
<span className="cargo-status">
{item.confidence || "MEDIUM"}
</span>
</td>



</tr>


))


}



</tbody>



</table>



</div>



</div>









{/* AI FEED */}


<div className="operations-panel">


<h2 className="section-title">

Pending AI Optimization Recommendations

</h2>



<div className="candidate-list">

{
recommendations.length === 0 ? (

<div className="candidate-card empty-ai-card">
<div>
<strong>No active AI recommendations</strong>
<p>All current cargo units are already allocated or stored.</p>
</div>
</div>

) : (

recommendations.slice(0,3).map((item,index)=>(

<div key={index} className="candidate-card">

<div className="candidate-header">

<div>
<strong>{item.cargo_reference || `Cargo ${item.cargo_id}`}</strong>

<span>
{item.cargo_type || "MANIFEST"} • {item.cargo_category || "GENERAL"}
</span>

</div>

</div>


<div className="recommendation-grid">

<div>
<label>Recommended Position</label>
<strong className="success-text">
#{item.position || item.recommended_position}
</strong>
</div>


<div>
<label>Weight</label>
<strong>
{Number(item.weight || 0).toLocaleString()} kg
</strong>
</div>


<div>
<label>Handling</label>
<strong>
{item.handling_method || "STANDARD"}
</strong>
</div>


<div>
<label>AI Confidence</label>
<strong>
{item.confidence || "MEDIUM"}
</strong>
</div>


</div>


<div className="ai-explanation">

<label>Why this position?</label>

{item.decision_reason && (
<div>
{(Array.isArray(item.decision_reason) ? item.decision_reason : [item.decision_reason])
.map((reason,i)=>(
<p key={i}>✓ {reason}</p>
))}
</div>
)}

</div>


<div className="recommendation-footer">

<span>
AI Score: {item.ai_score ?? "N/A"}
</span>

<span>
{item.method || "AI_RECOMMENDED"}
</span>

</div>


</div>

))

)

}

</div>


</div>


</div>


);


}







function Metric({

icon,

title,

value

}){


return (


<div className="metric-card">


<div className="metric-top">


{icon}


<span>

{title}

</span>


</div>



<strong>

{value}

</strong>



<p>

Current AI analysis

</p>



</div>


);


}