import api from "./axios";


const aiApi = {



    dashboard(){

    return api.get(
        "/dashboard/ai"
    );

    },



    decisions(){

    return api.get(
        "/reports/ai"
    );

    },


};



export default aiApi;