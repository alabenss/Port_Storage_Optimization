import api from "./axios";


const cargoApi = {


// ==========================
// GET ALL CARGO
// ==========================

getAll(){

    return api.get(
        "/cargo/"
    );

},


// ==========================
// GET DETAILS
// ==========================

getDetails(id){

    return api.get(
        `/cargo/${id}/details`
    );

},


// ==========================
// CREATE MANUAL CARGO
// ==========================

create(data){

    return api.post(
        "/cargo/manual",
        data
    );

},


// ==========================
// UPDATE CARGO
// ==========================

update(id,data){

    return api.put(
        `/cargo/${id}`,
        data
    );

},


// ==========================
// DELETE CARGO
// ==========================

delete(id){

    return api.delete(
        `/cargo/${id}`
    );

},


// ==========================
// SEARCH
// ==========================

search(query){

    return api.get(
        `/cargo/search/${query}`
    );

},


// ==========================
// AI RECOMMENDATION PREVIEW ONLY
// ==========================

recommendAI(id){

    return api.post(
        `/storage/recommend/${id}`
    );

},


// ==========================
// AI FINAL ALLOCATION
// ==========================

allocateAI(id){

    return api.post(
        `/storage/allocate/recommended/${id}`
    );

},


// ==========================
// RELEASE STORAGE
// ==========================

releaseStorage(id){

    return api.post(
        `/storage/release/cargo/${id}`
    );

}


};


export default cargoApi;