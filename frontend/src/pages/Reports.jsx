import React from "react";
import {
  FileText,
  Warehouse,
  Activity,
  Brain,
  Download,
  FileSpreadsheet,
  FileDown
} from "lucide-react";

import reportApi from "../api/reportApi";

import "../App.css";


function Reports() {


  const downloadFile = async (type, format) => {

    try {

      let response;


      if (format === "json") {

        const apiMap = {
          inventory: reportApi.inventory,
          storage: reportApi.storage,
          movements: reportApi.movements,
          ai: reportApi.ai
        };


        response = await apiMap[type]();


        const blob = new Blob(
          [JSON.stringify(response.data, null, 2)],
          {
            type:"application/json"
          }
        );


        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = url;

        link.download = `${type}_report.json`;

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);

        return;

      }



      if(format === "pdf") {

        response = await reportApi.pdf(type);

      }



      if(format === "excel") {

        response = await reportApi.excel(type);

      }



      const blob = new Blob(
        [response.data]
      );


      const url = window.URL.createObjectURL(blob);


      const link = document.createElement("a");


      link.href = url;


      link.download =
        `${type}_report.${format === "pdf" ? "pdf" : "xlsx"}`;


      document.body.appendChild(link);


      link.click();


      link.remove();


      window.URL.revokeObjectURL(url);



    }
    catch(error){

      console.error(error);

      alert(
        "Unable to export report"
      );

    }


  };





  const reports = [

    {
      title:"Inventory Report",

      icon:<FileText size={32}/>,

      description:
      "Current cargo inventory status and registered units.",

      includes:[
        "Cargo references",
        "Weight information",
        "Cargo status",
        "Categories"
      ],

      type:"inventory"
    },



    {
      title:"Storage Report",

      icon:<Warehouse size={32}/>,

      description:
      "Storage utilization and cargo placement information.",

      includes:[
        "Storage positions",
        "Occupied areas",
        "Available capacity",
        "Stored cargo"
      ],

      type:"storage"
    },



    {
      title:"Movement Report",

      icon:<Activity size={32}/>,

      description:
      "Cargo movement and operational activity history.",

      includes:[
        "Allocations",
        "Cargo movements",
        "Operations history",
        "Activity tracking"
      ],

      type:"movements"
    },



    {
      title:"Decision Report",

      icon:<Brain size={32}/>,

      description:
      "Operational decisions and optimization records.",

      includes:[
        "AI recommendations",
        "Allocation decisions",
        "Optimization history",
        "System actions"
      ],

      type:"ai"
    }

  ];




return (

<div>


<div className="page-header">




<h1>
Reports Center
</h1>


<p>
Operational data export and terminal activity summaries
</p>


</div>





<div className="panel">


<h2>
Report Overview
</h2>


<div className="storage-stats">


<div>

<span>
Available Reports
</span>


<strong>
4
</strong>

</div>




<div>

<span>
Active Export
</span>


<strong>
JSON / PDF / Excel
</strong>

</div>




<div>

<span>
Connected
</span>


<strong>
BACKEND
</strong>

</div>


</div>


</div>






<div
style={{
marginTop:"30px",
display:"grid",
gridTemplateColumns:"repeat(2,1fr)",
gap:"25px"
}}
>


{
reports.map((report)=>(


<div
key={report.type}
className="panel"
style={{
background:"#020617"
}}
>



<div
style={{
color:"#06b6d4",
marginBottom:"15px"
}}
>

{report.icon}

</div>




<h2>
{report.title}
</h2>




<p
style={{
color:"#94a3b8"
}}
>
{report.description}
</p>




<h3>
Includes
</h3>



<ul>

{
report.includes.map(item=>(

<li key={item}>
{item}
</li>

))
}

</ul>





<div
style={{
display:"flex",
gap:"12px",
marginTop:"25px",
flexWrap:"wrap"
}}
>



<button
onClick={()=>
downloadFile(report.type,"json")
}
>

<Download size={18}/>

Export JSON

</button>





<button
onClick={()=>
downloadFile(report.type,"pdf")
}
>

<FileDown size={18}/>

Export PDF

</button>





<button
onClick={()=>
downloadFile(report.type,"excel")
}
>

<FileSpreadsheet size={18}/>

Export Excel

</button>



</div>



</div>



))
}



</div>





</div>


);


}



export default Reports;