import { useEffect, useState } from "react";

import {
  Package,
  MapPin,
  CheckCircle,
  AlertTriangle
} from "lucide-react";

import api from "../api/axios";



export default function ManualAllocation(){


const [cargo,setCargo]=useState([]);

const [positions,setPositions]=useState([]);


const [selectedCargo,setSelectedCargo]=useState("");

const [selectedPosition,setSelectedPosition]=useState("");

const [message,setMessage]=useState(null);

const selectedCargoData =
cargo.find(c => String(c.id) === String(selectedCargo));

const [cargoSearch, setCargoSearch] = useState("");
const [positionSearch, setPositionSearch] = useState("");

const filteredCargo = cargo.filter(c =>
    (c.reference || "")
    .toLowerCase()
    .includes(cargoSearch.toLowerCase())
);

const filteredPositions = positions.filter(p =>
    (p.position_code || "")
    .toLowerCase()
    .includes(positionSearch.toLowerCase())
);

const selectedPositionData =
positions.find(p => String(p.id) === String(selectedPosition));




async function loadData(){


try{


const cargoRes =
await api.get("/cargo");


const positionRes =
await api.get("/storage/positions");



setCargo(
    cargoRes.data.filter(
        c => 
        c.status !== "STORED" &&
        c.status !== "ALLOCATED"
    )
);

setPositions(positionRes.data);



}catch(error){

console.log(error);

}


}





useEffect(()=>{

loadData();

},[]);








async function allocate(){

if(isCapacityExceeded){

setMessage({
type:"error",
text:"Cargo weight exceeds position capacity"
});

return;

}




if(!selectedCargo || !selectedPosition){

setMessage({

type:"error",

text:"Select cargo and position"

});


return;

}





try{


const response =

await api.post(

"/storage/allocate/manual",

{


cargo_id:
selectedCargo,


position_id:
selectedPosition


}

);




setMessage({

type:"success",

text:"Cargo allocated successfully"

});

await loadData();
setSelectedCargo("");
setSelectedPosition("");



}catch(error){


setMessage({

type:"error",

text:
error.response?.data?.detail
||
"Allocation failed"

});


}



}







const isCapacityExceeded =
Number(selectedCargoData?.weight || 0) >
Number(selectedPositionData?.max_weight || 0);


return (

<div className="cargo-page">

<div className="page-header">
<h1>Manual Allocation Center</h1>
<p>Operator controlled cargo placement</p>
</div>


<div className="dashboard-grid">


<div className="panel">

<h2> Select Cargo</h2>

<input
className="input"
placeholder="🔍 Search cargo..."
value={cargoSearch}
onChange={e=>setCargoSearch(e.target.value)}
/>

<select
className="input"
value={selectedCargo}
onChange={e=>setSelectedCargo(e.target.value)}
>

<option value="">
Choose cargo
</option>

{
filteredCargo.map(c=>(

<option key={c.id} value={c.id}>

{c.reference} - {c.weight} kg

</option>

))
}

</select>


{
selectedCargoData &&

<div className="detail-section">

<h3>CARGO INFORMATION</h3>

<div className="details-grid">

<div className="detail-card">
<span>Reference</span>
<strong>{selectedCargoData.reference}</strong>
</div>

<div className="detail-card">
<span>Weight</span>
<strong>{selectedCargoData.weight} kg</strong>
<p>
Type: {selectedCargoData.cargo_type || "N/A"}
</p>
<p>
Status: {selectedCargoData.status || "N/A"}
</p>
</div>

</div>

</div>

}

</div>



<div className="panel">

<h2>Select Position</h2>


<input
className="input"
placeholder="🔍 Search position..."
value={positionSearch}
onChange={e=>setPositionSearch(e.target.value)}
/>

<select
className="input"
value={selectedPosition}
onChange={e=>setSelectedPosition(e.target.value)}
>

<option value="">
Choose position
</option>

{
filteredPositions.map(p=>(

<option
key={p.id}
value={p.id}
>
{p.position_code}
{" - "}
{p.max_weight} kg
{" - "}
{p.occupied ? "Occupied" : "Free"}
</option>

))
}

</select>



{
selectedPositionData &&

<div className="detail-section">

<h3>POSITION INFORMATION</h3>

<div className="details-grid">

<div className="detail-card">
<span>Position</span>
<strong>{selectedPositionData.position_code}</strong>
</div>


<div className="detail-card">
<span>Capacity</span>
<strong>{selectedPositionData.max_weight} kg</strong>
<p>
Status:
{selectedPositionData.occupied ? "🔴 Occupied" : "🟢 Available"}
</p>
</div>

</div>

</div>

}

</div>

</div>




{
selectedCargoData && selectedPositionData &&

<div className="panel" style={{marginTop:"25px"}}>

<h2>Allocation Preview</h2>


<div className="details-grid">

<div className="detail-card">
<span>Cargo</span>
<strong>{selectedCargoData.reference}</strong>
<p>{selectedCargoData.weight} kg</p>
</div>


<div className="detail-card">
<span>Position</span>
<strong>{selectedPositionData.position_code}</strong>
<p>{selectedPositionData.max_weight} kg capacity</p>
</div>

</div>

</div>

}




<button

onClick={allocate}



className="primary-button"

>

<CheckCircle/>

Confirm Allocation

</button>




{
message &&

<div className={
message.type==="success"
?
"success-text"
:
"error-text"
}>

{
message.type==="success"
?
<CheckCircle/>
:
<AlertTriangle/>
}

{message.text}

</div>

}


</div>

)


}