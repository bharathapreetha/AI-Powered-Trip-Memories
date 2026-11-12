import { useEffect, useState } from 'react'
import ooty from './assets/ooty.jpg'
import axios from 'axios'
import './App.css'

import TripChat from "./TripChat";

/* const InitialTrip =[
  {
    id:1,
    name:"Ooty",
    image:ooty,
    notes:"Misty Mountain"
  },
  {
    id:2,
    name:"Pondy",
    image: pondy,
    notes:"Beach view from Room, wow awesome"
  }
] */

function App() {
  const[trips,setTrips]=useState([])
  const [showModel, setShowModel] = useState(false)
  const[placeName,setPlaceName] = useState('')
  const [notes,setNotes] = useState('')
  const[imagePreview,setImagePreview] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)

  /** Expense Section Stats */
  const [expenses, setExpenses] = useState([])
  const [expenseTitle , setExpenseTitle] = useState('')
  const [expenseAmount , setExpenseAmount] = useState('')

  /** Chat data */
  const [showChat, setShowChat] = useState(false)

  //Save Expense
  const saveExpense = () => {
    if(!expenseTitle.trim() || expenseAmount ===""){
      alert("Please Enter Expense Title and Amount")
      return;
    }

    const amount = Number(expenseAmount);
    if(!Number.isFinite(amount) || amount <=0){
      alert("Please Enter Valid Expense AMount");
      return;
    }

    const newExpense = {
      id:Date.now(),
      expense_name : expenseTitle.trim(),
      expense_amount : amount
    }
    setExpenses((current_exp) => [...current_exp,newExpense]);
  }

  useEffect(()=>{
    axios.get('http://127.0.0.1:8000/trips').then((response)=>{
      setTrips(response.data)
    }).catch((err)=>{
      console.log("Error Fetching Trips",err)
    })
  },[])


  function resetForm(){
    setPlaceName('')
    setImagePreview('')
    setNotes('')

    setExpenseTitle('')
    setExpenseAmount('')
    setExpenses([])
  }

  function closeModel() {
    setShowModel(false);
    resetForm();
  }

  //Image Handle
  function handleImageChange(event){
    const file=event.target.files[0]
    if (file) {
        setSelectedImage(file)
        setImagePreview(URL.createObjectURL(file))
    }
  }

  //Fetch trip from DB
  async function fetchTrips(){
    try{
      const response = await axios.get("http://127.0.0.1:8000/trips");
      setTrips(response.data);
    }catch(err){
      console.error("Error Fetching Trip data",err)
    }
  }

  //handle submit
  async function handleSubmit(event){
    event.preventDefault();

    if(!placeName.trim()){
      alert("Enter Place Name ")
      return;
    }
    try{
   /*    const newTrip ={
        place_name:placeName.trim(),
        image : imagePreview || ooty,
        notes: notes.trim(),
          expenses: expenses.map((expense)=>({
            expense_name : expense.e_title,
            expense_amount : expense.e_amount
          }))
      };
        //post request to FAST API 
      await axios.post("http://127.0.0.1:8000/trips", newTrip);
      await fetchTrips();
      */

      const formData = new FormData()
      formData.append("place_name", placeName)
      formData.append("notes",notes)
      formData.append("expenses", JSON.stringify(expenses))
     /*  formData.append(
          "expenses",
          JSON.stringify(
              expenses.map((expense) => ({
                  expense_name: expense.e_title,
                  expense_amount: expense.e_amount
              }))
          )
      ); */

      if(selectedImage){
        formData.append("image", selectedImage)
      }

      const response = await axios.post(
        "http://127.0.0.1:8000/trips",
        formData
      );

      console.log(response.data);
      alert('Trip added Successfully!')
      await fetchTrips();
      closeModel();
    }catch (err){
      console.error("Error adding trip:", err)
      console.error("Backend error:", err.response?.data)
      alert(err.response?.data?.detail || "Unable to add Trip")
    }
  }

  return (
    <>
      <section id="center">
        <div className="home">
          <h1 className="main_title"> Welcome to my <br/> AI Powered Trip Memories..! </h1>
          <button className="add-trip" onClick={()=> setShowModel(true)}>Add Place</button>
          {showModel && (
            <div className="model-overlay">
            <div className="place-model" role="dialog" aria-model="true" aria-labelledby="model-title" onClick={(event)=> event.stopPropagation()}>
              <div className="model-header">
                <h2 id="model-title">Add New Place</h2>
                <button type="button" className="close-btn" onClick={closeModel} aria-label="Close Popup"> x </button>
              </div>
              <form onSubmit={handleSubmit}>
                <label htmlFor="PlaceName"> Place Name </label>
                <input id="PlaceName" type="text" value={placeName} placeholder="India" onChange={(event)=> setPlaceName(event.target.value)} required /> 

                <label htmlFor="PlacePhoto" className="upload-label"> Place Photo </label>
                <input id="PlacePhoto" type="file" accept="image/*" onChange={handleImageChange}/>
                 { imagePreview && (
                  <img className="image-preview" src={imagePreview} alt="selected trip" />
                 )}
                <label htmlFor="PlaceNote"> Notes to Cherish </label>
                <textarea id="PlaceNote" placeholder="Write what you have seen,experienced" value={notes} onChange={(event)=>setNotes(event.target.value)} rows="3" />

                {/* Expenses Section */}
                <div className="expense-section">
                  <div className="expense-header">
                      <h3> Trip Expense </h3>
                  </div>

                  <div className="expense-form">
                    <input type="text" placeholder="Ex : Flight" value={expenseTitle} onChange={(e) => setExpenseTitle(e.target.value)}/>
                    <input type="Number" placeholder="Amount" min="0" step="10" value={expenseAmount} onChange={(e) => setExpenseAmount(e.target.value)} />
                    <button type="button" className="expense-add-btn" onClick={saveExpense}> Add Expense </button>
                  </div>

                  {/* Expense List*/}
                  <div className="expense-list">
                  {expenses.map((expense) => (
                      <div className="expense-card">
                        <div className="expense-info">
                          <strong>{expense.expense_name}</strong>
                          <span> {expense.expense_amount}</span>
                        </div>
                        <div className="expense-actions">
                          <button type="button" className="expense-edit-btn">Edit</button>
                          <button type="button" className="expense-delete-btn">Delete</button>
                        </div>
                      </div>
                     ))}
                  </div>
                </div>

                  <div className="model-footer">
                    <button type="submit" className="submit-btn"> Submit </button>
                  </div>
              </form>
            </div>
            </div>
          )}
          <div className="trip-list">
          {trips.map((trip) => ( 
            <div className="trip-set" key={trip.id}>
              <img src={`http://127.0.0.1:8000/${trip.image_path}`} alt={trip.place_name} />
              <h2>{trip.place_name}</h2>
              <p>{trip.notes}</p>
            </div>
          ))}
          </div>
        </div>
      </section>

      {/** FLoating Chat Icon */}
      {!showChat && (
      <button className="chat_icon" onClick={() => setShowChat(!showChat)}> 💬 </button>
      )}

       {/** Chat Sidebar */}
       {showChat && (
        <div className="chat_sidebar">
            <div className="chat_header">
              <h3> Trip Memory </h3>
              <button onClick={()=> setShowChat(false)}> X </button>
            </div>

            <div className="chat_body">
              <TripChat />
            </div>
        </div>
       )}
    </>
  )
}
export default App