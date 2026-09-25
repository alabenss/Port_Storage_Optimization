import { 
    useEffect, 
    useState 
} from "react"; 
 
 
import { 
    Plus, 
    Pencil, 
    Trash2, 
    Brain, 
    Search, 
    Eye, 
    X, 
    Package, 
    Weight, 
    CheckCircle, 
    AlertTriangle, 
    Sparkles, 
    MapPin, 
    FileText, 
    ShieldCheck, 
    Filter, 
    Calendar, 
    Box 
} from "lucide-react"; 
 
 
import cargoApi from "../api/cargoApi"; 
 
import { useModal } from "../context/ModalContext";
 
 
export default function Cargo(){ 
 
const {
    showAlert,
    confirm
} = useModal();

const emptyForm = { 
 
    reference:"", 
    cargo_type:"", 
    cargo_category:"", 
    weight:"", 
    status:"IMPORTED", 
    bl_number:"", 
    quantity:1, 
    length:"", 
    width:"", 
    height:"" 
 
}; 
 
 
 
const [cargo,setCargo] = useState([]); 
 
const [loading,setLoading] = useState(true); 
 
 
const [search,setSearch] = useState(""); 
 
const [typeFilter,setTypeFilter] = useState(""); 
 
const [statusFilter,setStatusFilter] = useState(""); 
 
const [minWeight,setMinWeight] = useState(""); 
 
const [maxWeight,setMaxWeight] = useState(""); 
 
const [weightSort,setWeightSort] = useState(""); 
 
 
 
const [showForm,setShowForm] = useState(false); 
 
const [showDetails,setShowDetails] = useState(false); 
 
const [showAI,setShowAI] = useState(false); 
 
const [showDelete,setShowDelete] = useState(false); 
 
 
 
const [selectedCargo,setSelectedCargo] = useState(null); 
 
const [details,setDetails] = useState(null); 
 
const [aiResult,setAIResult] = useState(null);

const [loadingAction,setLoadingAction] = useState(null);

const [processing,setProcessing] = useState(false); 
 
 
 
const [editId,setEditId] = useState(null); 
 
 
const [form,setForm] = useState(emptyForm); 
 
 
 
 
 
async function loadCargo(){ 
 
    try{ 
 
        setLoading(true); 
 
        const response = 
        await cargoApi.getAll(); 
 
 
        setCargo(response.data); 
 
 
    } 
    catch(error){ 
 
        console.log(error); 
 
    } 
    finally{ 
 
        setLoading(false); 
 
    } 
 
} 
 
 
 
 
 
useEffect(()=>{ 
 
    loadCargo(); 
 
},[]); 
 
 
 
 
 
 
 
async function saveCargo(){


    try{


        if(
            !form.reference ||
            !form.cargo_category ||
            !form.weight
        ){

            showAlert("Please fill all required fields");
            return;

        }



        const payload = {

            reference: form.reference,

            cargo_type: "MANUAL",

            cargo_category: form.cargo_category,

            weight: Number(form.weight),

            quantity: Number(form.quantity || 1),

            length: form.length || null,

            width: form.width || null,

            height: form.height || null,

            bl_number: form.bl_number,

            status: "IMPORTED"

        };



        console.log("SENDING CARGO:", payload);



        if(editId){


            await cargoApi.update(
                editId,
                payload
            );


        }
        else{


            await cargoApi.create(
                payload
            );


        }



        setShowForm(false);

        setEditId(null);

        setForm(emptyForm);


        await loadCargo();


    }
    catch(error){

        console.log(
            "FULL ERROR:",
            error
        );


        console.log(
            "BACKEND RESPONSE:",
            error.response?.data
        );


        const message =
            error.response?.data?.detail
            ? JSON.stringify(
                error.response.data.detail
              )
            :
            JSON.stringify(
                error.response?.data
              )
            ||
            error.message;


        showAlert(message);

    }



}





function openEdit(item){ 
 
 
    setEditId(item.id); 
 
 
    setForm({ 
 
        ...emptyForm, 
 
        ...item, 
 
        cargo_category: 
        item.cargo_category || 
        item.category || 
        "" 
 
    }); 
 
 
    setShowForm(true); 
 
 
} 
 
 
 
 
 
 
 
async function openDetails(id){ 
 
 
    try{ 
 
 
        const response = 
        await cargoApi.getDetails(id); 
 
 
 
        setDetails(response.data); 
 
 
        setShowDetails(true); 
 
 
 
    } 
    catch(error){ 
 
        console.log(error); 
 
    } 
 
 
} 
 
 
 
 
 
 
 
function askDelete(item){ 
 
 
    setSelectedCargo(item); 
 
 
    setShowDelete(true); 
 
 
} 
 
 
 
 
 
async function confirmDelete(){ 
 
 
    try{ 
 
 
        await cargoApi.delete( 
            selectedCargo.id 
        ); 
 
 
        setShowDelete(false); 
 
 
        setSelectedCargo(null); 
 
 
        loadCargo(); 
 
 
 
    } 
    catch(error){ 
 
        console.log(error); 
 
    } 
 
 
} 
 
 
 
 
 
async function runAI(id){

    try{

        const response =
        await cargoApi.recommendAI(id);

        setSelectedCargo(
            cargo.find(
                item => item.id === id
            )
        );

        setAIResult(response.data);

        setShowAI(true);

    }
    catch(error){

        console.log(error);

    }

} 


async function confirmAIAllocation(){

    try{

        if(!selectedCargo){
            return;
        }


        const response =
        await cargoApi.allocateAI(
            selectedCargo.id
        );


        setAIResult(
            response.data
        );


        await loadCargo();


    }
    catch(error){

        console.log(
            error.response?.data || error
        );

    }

}


async function releaseCargo(id){

    try{

        setProcessing(true);

        setLoadingAction(id);


        await cargoApi.releaseStorage(id);


        await loadCargo();


    }
    catch(error){

        console.log(
            error.response?.data || error
        );

    }
    finally{

        setProcessing(false);

        setLoadingAction(null);

    }

}


function translateAIStatus(status){

    const map = {

        "ALREADY_ALLOCATED":
        "This cargo is already stored.",

        "POSITION_RECOMMENDED":
        "AI recommendation generated.",

        "PLAN_READY":
        "Storage position selected. Waiting for confirmation.",

        "MULTI_POSITION_RECOMMENDED":
        "AI selected multiple storage positions.",

        "INSUFFICIENT_STORAGE_CAPACITY":
        "The required storage area does not have enough available capacity.",

        "NO_STORAGE_PLAN":
        "No compatible storage position was found.",

        "ALLOCATION_FAILED":
        "Storage allocation failed."

    };

    return map[status] || status || "AI analysis completed";

}


function translateZone(value){ 
 
 
    const map = { 
 
 
        "PACKAGE_AREA": 
        "Package Storage Area", 
 
 
        "PACKAGE": 
        "Package Storage Area", 
 
 
        "PACKAGE_STACK": 
        "Package Stack Position", 
 
 
        "CONTAINER_YARD": 
        "Container Yard", 
 
 
        "CONTAINER_SLOT": 
        "Container Storage Slot", 
 
 
        "VEHICLE_YARD": 
        "Vehicle Yard", 
 
 
        "VEHICLE_SLOT": 
        "Vehicle Parking Slot", 
 
 
        "COIL_AREA": 
        "Coil Storage Area", 
 
 
        "COIL_SLOT": 
        "Coil Storage Position", 
 
 
        "BULK_SILO_AREA": 
        "Bulk Silo Area", 
 
 
        "SILO": 
        "Bulk Silo" 
 
    }; 
 
 
    return map[value] || value || "-"; 
 
 
} 


function handleMinWeight(value){

    if(value !== "" && Number(value) < 0){
        setMinWeight("");
        return;
    }

    if(maxWeight !== "" && value !== "" && Number(value) > Number(maxWeight)){
        return;
    }

    setMinWeight(value);

}


function handleMaxWeight(value){

    if(value !== "" && Number(value) < 0){
        setMaxWeight("");
        return;
    }

    if(minWeight !== "" && value !== "" && Number(value) < Number(minWeight)){
        return;
    }

    setMaxWeight(value);

}


function filteredCargoList(){


    return cargo.filter(item=>{


        const referenceMatch =

        item.reference
        ?.toLowerCase()
        .includes(
            search.toLowerCase()
        );



        const typeMatch =

        !typeFilter ||

        item.cargo_type === typeFilter;



        const statusMatch =

        !statusFilter ||

        item.status === statusFilter;



        const weight =

        Number(item.weight || 0);



        const minMatch =

        !minWeight ||

        weight >= Number(minWeight);



        const maxMatch =

        !maxWeight ||

        weight <= Number(maxWeight);



        return (

            referenceMatch &&

            typeMatch &&

            statusMatch &&

            minMatch &&

            maxMatch

        );


    });


}




const filteredCargo = filteredCargoList();


const sortedCargo = [...filteredCargo].sort((a,b)=>{

    if(weightSort==="asc"){
        return Number(a.weight||0) - Number(b.weight||0);
    }

    if(weightSort==="desc"){
        return Number(b.weight||0) - Number(a.weight||0);
    }

    return 0;

});





const totalWeight =


cargo.reduce(

    (sum,item)=>

    sum +

    Number(item.weight || 0),

    0

);





const cargoTypes =

[
    ...new Set(

        cargo.map(
            item=>item.cargo_type
        )

    )
];





const cargoStatuses =

[
    ...new Set(

        cargo.map(
            item=>item.status
        )

    )
];







return (

<div className="dashboard cargo-page">





<div className="page-header">


<p className="page-label">

CARGO CONTROL CENTER

</p>


<h1>

Cargo Management

</h1>


<p>

Terminal cargo inventory, tracking and AI storage optimization

</p>


</div>









<div className="kpi-grid">



<div className="metric-card">


<div className="metric-top">

<Package/>

<span>

TOTAL CARGO

</span>

</div>


<strong>

{cargo.length}

</strong>


<p>

Registered cargo units

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

{

(totalWeight / 1000000)

.toFixed(2)

}M

</strong>


<p>

Metric tons

</p>


</div>







<div className="metric-card">


<div className="metric-top">

<ShieldCheck/>

<span>

INVENTORY

</span>

</div>


<strong>

ACTIVE

</strong>


<p>

Database synchronized

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

READY

</strong>


<p>

Optimization available

</p>


</div>




</div>









<div className="panel">



<div className="cargo-toolbar">


<div>


<h2>

Cargo Inventory

</h2>


<p>

Manage all terminal cargo operations

</p>


</div>





<button

className="primary-button"

onClick={()=>{


setEditId(null);

setForm(emptyForm);

setShowForm(true);


}}

>


<Plus size={18}/>

Add Cargo


</button>



</div>









<div className="cargo-filters">



<div className="search-box">


<Search/>


<input

placeholder="Search reference..."

value={search}

onChange={e=>

setSearch(e.target.value)

}


/>


</div>







<div className="filter-item">


<Filter size={17}/>


<select

value={typeFilter}

onChange={e=>

setTypeFilter(e.target.value)

}

>


<option value="">

All Types

</option>


{

cargoTypes.map(type=>(

<option

key={type}

value={type}

>

{type}

</option>


))

}


</select>


</div>







<div className="filter-item">


<select

value={statusFilter}

onChange={e=>

setStatusFilter(e.target.value)

}

>


<option value="">

All Status

</option>


{

cargoStatuses.map(status=>(

<option

key={status}

value={status}

>

{status}

</option>


))

}


</select>


</div>







<div className="weight-filter">


<input

type="number"

min="0"

placeholder="Min weight (kg)"

value={minWeight}

style={{width:"120px"}}

onChange={e=>

handleMinWeight(e.target.value)

}


/>



<input

type="number"

min="0"

placeholder="Max weight (kg)"

value={maxWeight}

style={{width:"120px"}}

onChange={e=>

handleMaxWeight(e.target.value)

}


/>


</div>







<div className="filter-item">


<select

value={weightSort}

onChange={e=>

setWeightSort(e.target.value)

}

>


<option value="">

Sort by default

</option>


<option value="asc">

Weight: Lowest → Highest

</option>


<option value="desc">

Weight: Highest → Lowest

</option>


</select>


</div>





</div><table className="cargo-table">


<thead>

<tr>


<th>

Reference

</th>


<th>

Type

</th>


<th>

Category

</th>


<th>

Weight

</th>


<th>

Status

</th>


<th>

Actions

</th>


</tr>


</thead>





<tbody>


{


loading ?


<tr>

<td

colSpan="6"

className="loading-cell"

>

Loading cargo database...

</td>

</tr>



:



sortedCargo.map(item=>(


<tr

key={item.id}

>





<td>


<div className="cargo-reference">


<Package size={16}/>


<strong>

{item.reference}

</strong>


</div>


</td>








<td>

{item.cargo_type || "-"}

</td>






<td>

{

item.cargo_category ||

item.category ||

"-"

}

</td>






<td>


<div className="weight-cell">


<Weight size={15}/>


{

Number(item.weight || 0)

.toLocaleString()

}

kg


</div>


</td>







<td>


<span

className={

`status-badge status-${

item.status

?.toLowerCase()

}`

}

>


{item.status}


</span>


</td>







<td>


<div className="cargo-actions">



<button


className="action-view"


title="View details"


onClick={()=>openDetails(item.id)}


>


<Eye size={17}/>


</button>








<button


className="action-edit"


title="Edit cargo"


onClick={()=>openEdit(item)}


>


<Pencil size={17}/>


</button>








<button


className="action-delete"


title="Delete cargo"


onClick={()=>askDelete(item)}


>


<Trash2 size={17}/>


</button>








{
item.status === "STORED" && (

<button


className="action-release"


title="Release storage position"


disabled={loadingAction===item.id}


onClick={()=>releaseCargo(item.id)}


>


{
loadingAction===item.id
?

"..."

:

<Package
size={17}
color="#22d3ee"
/>

}


</button>

)
}





{
item.status === "IMPORTED" && (

<button


className="action-ai"


title="AI recommendation"


onClick={()=>runAI(item.id)}


>


<Brain size={17}/>


</button>

)
}





</div>


</td>




</tr>



))


}



</tbody>


</table>






</div>
















{
showForm &&



<div className="modal-overlay">


<div className="modal cargo-modal">





<div className="modal-header">


<div>


<h2>

{

editId ?

"Edit Cargo"

:

"Register New Cargo"

}

</h2>


<p>

Enter cargo information

</p>


</div>




<X

cursor="pointer"

onClick={()=>setShowForm(false)}

/>


</div>








<div className="form-grid">



<input

placeholder="Reference"

value={form.reference}

onChange={e=>

setForm({

...form,

reference:e.target.value

})

}

/>






<select

value={form.cargo_category}

onChange={e=>

setForm({

    ...form,

    cargo_category:e.target.value

})

}

>

<option value="">
Cargo Category
</option>

<option value="PACKAGE">
Package
</option>

<option value="CONTAINER">
Container
</option>

<option value="VEHICLE">
Vehicle
</option>

<option value="COIL">
Coil
</option>

</select>
















<input

type="number"

placeholder="Weight (kg)"

value={form.weight}

onChange={e=>

setForm({

...form,

weight:Number(e.target.value)

})

}

/>







<input

type="number"

placeholder="Quantity"

value={form.quantity}

onChange={e=>

setForm({

...form,

quantity:e.target.value

})

}

/>







<input

placeholder="BL Number"

value={form.bl_number}

onChange={e=>

setForm({

...form,

bl_number:e.target.value

})

}

/>




</div>









<button


className="primary-button full"


onClick={saveCargo}


>


<CheckCircle size={18}/>


Save Cargo


</button>





</div>


</div>


}{
showAI && aiResult &&


<div className="modal-overlay">


<div className="modal ai-modal">





<div className="modal-header">


<div className="ai-title">


<Sparkles/>


<div>

<h2>

AI Storage Optimization

</h2>


<p>

Smart allocation recommendation

</p>


</div>


</div>





<X

onClick={()=>setShowAI(false)}

className="cursor-pointer"

/>


</div>









<div className="ai-summary">



<h3>

Cargo Decision

</h3>



<div className="ai-status-box">


{

aiResult.status === "SUCCESS" ||

aiResult.status === "ALLOCATED" ||

aiResult.status === "PLAN_READY"

?


<CheckCircle/>


:


<AlertTriangle/>


}



<div>


<strong>

{

aiResult.status === "SUCCESS" ||

aiResult.status === "ALLOCATED" ||

aiResult.status === "PLAN_READY"

?

"AI Recommendation Ready"

:

"Recommendation Issue"

}

</strong>


<p>

{

translateAIStatus(aiResult.status)

}

</p>


</div>



</div>



</div>









{
aiResult.status === "PLAN_READY" && (

<button
className="primary-button full"
onClick={confirmAIAllocation}
style={{
marginBottom:"20px"
}}
>

<CheckCircle size={18}/>

Confirm AI Allocation

</button>

)
}


<div className="ai-info-grid">



<div>


<span>

Recommended Zone

</span>


<strong>

{

translateZone(

aiResult.required_zone_type

)

}

</strong>


</div>







<div>


<span>

Position Type

</span>


<strong>

{

translateZone(

aiResult.required_position_type

)

}

</strong>


</div>







<div>


<span>

Remaining Capacity

</span>


<strong>

{
aiResult.remaining_weight ??
aiResult.remaining_unallocated_weight ??
0
}

kg

</strong>


</div>



</div>


<h3 className="section-title">

{
(aiResult.status === "SUCCESS" ||
 aiResult.status === "ALLOCATED" ||
 aiResult.status === "PLAN_READY")

?

"Allocated Storage Positions"

:

"Allocation Analysis"

}

</h3>


{
(
    aiResult.allocations ||
    aiResult.selected_position_details ||
    []
).length > 0

?

<div className="candidate-list">

{
(
    aiResult.allocations ||
    aiResult.selected_position_details ||
    []
).map((position,index)=>(

<div
className="candidate-card"
key={index}
>


<div>

<MapPin size={18}/>

<strong>

{
position.position?.position_code ||
position.position_code ||
"-"
}

</strong>

</div>



<p>

Zone:

{" "}

{
position.position?.zone?.name ||
position.zone ||
position.zone_name ||
"-"
}

</p>



<p>

Position Type:

{" "}

{
translateZone(
position.position?.position_type ||
position.position_type ||
position.type
)

}

</p>



<p>

Allocated Weight:

{" "}

<strong>

{

Number(
position.allocated_weight || 0
)
.toLocaleString()

}

kg

</strong>

</p>



<p className="ai-score">

Allocation Status:

SUCCESS

</p>


</div>

))

}

</div>


:


<div className="empty-ai">

<AlertTriangle/>

<p>

{
 aiResult.status === "NO_STORAGE_PLAN"

 ?

 "AI could not find a valid empty storage position."

 :

 aiResult.status === "INSUFFICIENT_STORAGE_CAPACITY"

 ?

 "Not enough available capacity for this cargo."

 :

 "No storage position allocated."
}

</p>

</div>

}





</div>


</div>


}












{
showDetails && details &&



<div className="modal-overlay">


<div className="modal details-modal">






<div className="modal-header">


<div>


<h2>

Cargo Details

</h2>


<p>

Complete cargo information

</p>


</div>



<X

onClick={()=>setShowDetails(false)}

className="cursor-pointer"

/>


</div>









<div className="details-grid">





<div className="detail-card">


<FileText/>


<span>

Reference

</span>


<strong>

{details.reference || "-"}

</strong>


</div>






<div className="detail-card">


<Package/>


<span>

Type

</span>


<strong>

{details.cargo_type || "-"}

</strong>


</div>






<div className="detail-card">


<Box/>


<span>

Category

</span>


<strong>

{

details.cargo_category ||

"-"

}

</strong>


</div>






<div className="detail-card">


<Weight/>


<span>

Weight

</span>


<strong>

{

details.weight ||

0

}

kg

</strong>


</div>






<div className="detail-card">


<Calendar/>


<span>

Arrival Date

</span>


<strong>

{

details.arrival_date ||

"-"

}

</strong>


</div>






<div className="detail-card">


<ShieldCheck/>


<span>

Status

</span>


<strong>

{

details.status ||

"-"

}

</strong>


</div>




</div>








<div className="details-section">


<h3>

Physical Characteristics

</h3>



<div className="characteristics">


<p>

Quantity:

<b>

{

details.quantity ||

1

}

</b>

</p>



<p>

Dimensions:

<b>

{

details.length || "-"

}

×

{

details.width || "-"

}

×

{

details.height || "-"

}

</b>

</p>




<p>

Stackable:

<b>

{

details.stackable

?

"YES"

:

"NO"

}

</b>

</p>



<p>

Storage Profile:

<b>

{

details.storage_profile ||

"-"

}

</b>

</p>



</div>


</div>


{

details.allocations && details.allocations.length > 0 && (

<div className="details-section">

<h3>

Storage & Movement Information

</h3>


<div className="characteristics">

<p>

Current Position:

<b>

{

details.allocations[0]?.position_code || "-"

}

</b>

</p>


<p>

Zone:

<b>

{

details.allocations[0]?.zone || "-"

}

</b>

</p>


<p>

Allocation Method:

<b>

{

details.allocations[0]?.allocation_method || "-"

}

</b>

</p>


<p>

Allocated Weight:

<b>

{

details.allocations[0]?.allocated_weight || 0

}

kg

</b>

</p>

</div>

</div>

)

}







</div>


</div>



}









{
showDelete && selectedCargo &&



<div className="modal-overlay">


<div className="modal delete-modal">





<div className="delete-icon">

<Trash2/>

</div>





<h2>

Delete Cargo?

</h2>



<p>

Are you sure you want to remove

<strong>

{" "}

{selectedCargo.reference}

{" "}

</strong>

from the terminal database?

</p>







<div className="delete-actions">


<button


className="secondary-button"


onClick={()=>{


setShowDelete(false);

setSelectedCargo(null);


}}


>


Cancel


</button>







<button


className="danger-button"


onClick={confirmDelete}


>


<Trash2 size={18}/>

Delete


</button>




</div>






</div>


</div>



}



{
processing && (

<div className="processing-overlay">

    <div className="processing-box">

        <Package size={30}/>

        <p>
            Updating storage allocation...
        </p>

    </div>

</div>

)
}


</div>


);


}
