import { useState } from "react";

import {
  UploadCloud,
  CheckCircle,
  Database,
  FileSpreadsheet,
  AlertTriangle,
} from "lucide-react";

import api from "../api/axios";


function ImportManifest() {


  const [file, setFile] = useState(null);

  const [result, setResult] = useState(null);

  const [imported, setImported] = useState(null);

  const [uploading, setUploading] = useState(false);

  const [confirming, setConfirming] = useState(false);

  const [activeTab, setActiveTab] = useState("bill_of_lading");



  // ==========================
  // UPLOAD + ANALYZE MANIFEST
  // ==========================

  const uploadManifest = async () => {


    if (!file)
      return;



    try {


      setUploading(true);



      const formData = new FormData();


      formData.append(
        "file",
        file
      );



      const response = await api.post(

        "/import/manifest",

        formData,

        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }

      );



      setResult(response.data);



    } catch (error) {


      console.error(error);

      alert(
        "Manifest analysis failed"
      );


    } finally {


      setUploading(false);


    }

  };






  // ==========================
  // CONFIRM DATABASE IMPORT
  // ==========================

  const confirmImport = async () => {


    if (!result?.upload_id)
      return;



    try {


      setConfirming(true);



      const response = await api.post(

        `/import/confirm?upload_id=${result.upload_id}`

      );



      setImported(
        response.data
      );



    } catch (error) {


      console.error(error);

      alert(
        "Import failed"
      );


    } finally {


      setConfirming(false);


    }


  };







  return (


    <div>



      <div className="page-header">


        <div>


          <p className="page-label">
            DATA IMPORT
          </p>


          <h1>
            Import Manifest
          </h1>


          <p>
            Upload, analyze and import vessel cargo manifests.
          </p>


        </div>


      </div>







      <section className="panel upload-panel">



        <UploadCloud size={45} />



        <h2>
          Upload Excel Manifest
        </h2>



        <p>
          Supported formats: XLSX / XLS
        </p>





        <input

          type="file"

          accept=".xlsx,.xls"

          onChange={(event) =>
            setFile(
              event.target.files[0]
            )
          }

        />





        {
          file &&

          <div className="selected-file">


            <FileSpreadsheet size={18}/>


            {file.name}


          </div>

        }







        <button

          className="primary-button"

          disabled={
            !file || uploading
          }

          onClick={uploadManifest}

        >


          {

            uploading

            ?

            "Analyzing..."

            :

            "Analyze Manifest"

          }


        </button>









        {
          result &&


          <div className="import-result">





            <h3>

              <CheckCircle size={20}/>

              Manifest Analysis Completed

            </h3>






            <p>

              Upload ID:

              <strong>

                {" "}
                {result.upload_id}

              </strong>

            </p>









            {

              result.can_import

              ?

              <p className="success-text">

                <CheckCircle size={18}/>

                Manifest validated successfully

              </p>


              :

              <p className="error-text">

                <AlertTriangle size={18}/>

                Validation failed

              </p>


            }









            <h3>
              Manifest Summary
            </h3>






            <div className="summary-grid">



              <div className="summary-card">

                <strong>
                  {
                    result.preview.summary.bill_of_lading
                  }
                </strong>

                <span>
                  Bill Of Lading
                </span>

              </div>






              <div className="summary-card">

                <strong>
                  {
                    result.preview.summary.vehicles
                  }
                </strong>

                <span>
                  Vehicles
                </span>

              </div>






              <div className="summary-card">

                <strong>
                  {
                    result.preview.summary.containers
                  }
                </strong>

                <span>
                  Containers
                </span>

              </div>






              <div className="summary-card">

                <strong>
                  {
                    result.preview.summary.trailers
                  }
                </strong>

                <span>
                  Trailers
                </span>

              </div>






              <div className="summary-card">

                <strong>
                  {
                    result.preview.summary.total_records
                  }
                </strong>

                <span>
                  Total Records
                </span>

              </div>



            </div>









            <div className="import-tabs">

              {[
                ["bill_of_lading","Bill Of Lading"],
                ["vehicles","Vehicles"],
                ["containers","Containers"],
                ["trailers","Trailers"],
                ["validation","Validation"]
              ].map(([key,label]) => (
                <button
                  key={key}
                  className={activeTab===key ? "active-tab" : ""}
                  onClick={() => setActiveTab(key)}
                >
                  {label}
                </button>
              ))}

            </div>


            <div className="preview-area">


            {activeTab==="bill_of_lading" && (

              <table className="preview-table">

                <thead>
                  <tr>
                    <th>BL Number</th>
                    <th>Cargo Nature</th>
                    <th>Description</th>
                    <th>Weight</th>
                    <th>Packages</th>
                  </tr>
                </thead>

                <tbody>

                {
                  result.preview.records.bill_of_lading?.map((item,index)=>(
                    <tr key={index}>
                      <td>{item.bl_number}</td>
                      <td>{item.cargo_nature}</td>
                      <td>{item.description}</td>
                      <td>{item.gross_weight}</td>
                      <td>{item.package_number}</td>
                    </tr>
                  ))
                }

                </tbody>

              </table>

            )}



            {activeTab==="vehicles" && (

              <table className="preview-table">
                <thead>
                  <tr>
                    <th>BL</th>
                    <th>Chassis</th>
                    <th>Manufacturer</th>
                    <th>Model</th>
                    <th>Year</th>
                    <th>Weight</th>
                  </tr>
                </thead>

                <tbody>

                {
                  result.preview.records.vehicles?.map((item,index)=>(
                    <tr key={index}>
                      <td>{item.bl_number}</td>
                      <td>{item.chassis_number}</td>
                      <td>{item.manufacturer}</td>
                      <td>{item.model}</td>
                      <td>{item.year}</td>
                      <td>{item.loaded_weight}</td>
                    </tr>
                  ))
                }

                </tbody>
              </table>

            )}



            {activeTab==="containers" && (

              <table className="preview-table">

                <thead>
                  <tr>
                    <th>BL</th>
                    <th>Container</th>
                    <th>Category</th>
                    <th>Packages</th>
                    <th>Weight</th>
                  </tr>
                </thead>

                <tbody>

                {
                  result.preview.records.containers?.map((item,index)=>(
                    <tr key={index}>
                      <td>{item.bl_number}</td>
                      <td>{item.container_number}</td>
                      <td>{item.category}</td>
                      <td>{item.package_number}</td>
                      <td>{item.gross_weight}</td>
                    </tr>
                  ))
                }

                </tbody>

              </table>

            )}



            {activeTab==="trailers" && (

              <table className="preview-table">

                <thead>
                  <tr>
                    <th>BL</th>
                    <th>Reference</th>
                    <th>Type</th>
                    <th>Weight</th>
                  </tr>
                </thead>

                <tbody>

                {
                  result.preview.records.trailers?.map((item,index)=>(
                    <tr key={index}>
                      <td>{item.bl_number}</td>
                      <td>{item.reference}</td>
                      <td>{item.trailer_type}</td>
                      <td>{item.weight}</td>
                    </tr>
                  ))
                }

                </tbody>

              </table>

            )}



            {activeTab==="validation" && (

              <div className="validation-panel">

                <h3>Warnings</h3>

                {
                  result.preview.validation.warnings.length
                  ?
                  result.preview.validation.warnings.map((w,i)=>
                    <p key={i}>{w}</p>
                  )
                  :
                  <p>No warnings</p>
                }


                <h3>Errors</h3>

                {
                  result.preview.validation.errors.length
                  ?
                  result.preview.validation.errors.map((e,i)=>
                    <p key={i}>{e}</p>
                  )
                  :
                  <p>No errors</p>
                }

              </div>

            )}

            </div>

            <button

              className="primary-button"

              disabled={
                !result.can_import ||
                confirming
              }

              onClick={confirmImport}

            >


              {

                confirming

                ?

                "Importing..."

                :

                "Confirm Database Import"

              }


            </button>







          </div>


        }









        {

          imported &&


          <div className="import-result success">



            <h3>

              <Database size={20}/>

              Import Completed

            </h3>




            <p>

              Status:

              <strong>

                {" "}
                {imported.status}

              </strong>

            </p>





            <p>

              File:

              <strong>

                {" "}
                {imported.file}

              </strong>

            </p>





          </div>


        }






      </section>





    </div>


  );

}



export default ImportManifest;