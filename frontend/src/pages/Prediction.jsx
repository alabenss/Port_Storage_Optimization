import {
    Brain,
    Package,
    Warehouse,
    BarChart3,
    AlertTriangle
} from "lucide-react";

export default function Prediction() {
    return (
        <div className="dashboard cargo-page">

            <div className="page-header">
                <h1>Terminal Prediction</h1>
                <p>
                    Data-driven analysis to support terminal operations
                </p>
            </div>


            <div className="panel">

                <div className="cargo-toolbar">
                    <div>
                        <h2>Prediction Modules</h2>
                        <p>Operational forecasting tools</p>
                    </div>
                    <Brain />
                </div>


                <div className="details-grid">


                    <div className="detail-card">
                        <Package />
                        <span>Cargo Dwell Time</span>
                        <strong>Prediction Model</strong>
                        <p>
                            Estimate expected storage duration
                            based on cargo history.
                        </p>
                    </div>


                    <div className="detail-card">
                        <Warehouse />
                        <span>Storage Occupancy</span>
                        <strong>Forecast</strong>
                        <p>
                            Analyze future storage area usage
                            and capacity requirements.
                        </p>
                    </div>


                    <div className="detail-card">
                        <BarChart3 />
                        <span>Terminal Activity</span>
                        <strong>Forecast</strong>
                        <p>
                            Predict operational workload
                            using historical movements.
                        </p>
                    </div>


                    <div className="detail-card">
                        <AlertTriangle />
                        <span>Operational Risk</span>
                        <strong>Analysis</strong>
                        <p>
                            Identify possible congestion
                            and operational constraints.
                        </p>
                    </div>


                </div>

            </div>



            <div className="panel" style={{marginTop:"25px"}}>

                <div className="cargo-toolbar">
                    <div>
                        <h2>Model Integration</h2>
                        <p>
                            Connect machine learning models with terminal data
                        </p>
                    </div>
                </div>


                <div className="ai-status-box">


                    <div>
                        <strong>Prediction System Ready</strong>

                        <p>
                            This section will display real predictions,
                            recommendations and analytics once models are connected.
                        </p>
                    </div>

                </div>

            </div>


        </div>
    );
}
