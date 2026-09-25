import api from "./axios";

const reportApi = {

    inventory: () =>
        api.get("/reports/inventory"),

    storage: () =>
        api.get("/reports/storage"),

    movements: () =>
        api.get("/reports/movements"),

    ai: () =>
        api.get("/reports/ai"),


    pdf: (report) =>
        api.get(`/reports/${report}/pdf`, {
            responseType: "blob"
        }),


    excel: (report) =>
        api.get(`/reports/${report}/excel`, {
            responseType: "blob"
        })

};


export default reportApi;