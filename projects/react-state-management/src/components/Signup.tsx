import { useReducer,useMemo,useCallback } from "react";

const initialState = {
    fields:{
        email:'',
        password:'',
        confirmPassword:'',
    },
    errors:{
        email:null,
        password:null,
        confirmPassword:null
    },
    touched:{
        email:false,
        password:false,
        confirmPassword:false
    }
}

const formReducer =(state,action)=>{
    switch(action.type){
        case 'UPDATE_FIELD':
            return{
                ...state,
                fields:{
                    ...state.fields,
                    [action.field]:action.value
                },
                //clear errors when user types
                errors:{
                    ...state.errors,
                    [action.field]: null
                }
            }
        case 'SET_TOUCHED':
            return {
                ...state, //copy the top level state
                touched:{
                    ...state.touched, //copy the nested touch object
                    [action.field]:true //set the specific field's 'touched' status to true
                }                                
            }
        case 'VALIDATE_FIELD':
            return {
                ...state,
                errors:{
                    ...state.errors,
                    [action.field]:action.error
                }
            }
        case 'SUBMIT_FORM':
            return{
                ...state,
                touched:{
                    email:true,
                    password:true,
                    confirmPassword:true
                },
                errors:{
                    email:action.errors.email,
                    password:action.errors.password,
                    confirmPassword:action.errors.confirmPassword
                }
            }
        default:
            return state
        }



    }

function SignupForm() {
  const [state, dispatch] = useReducer(formReducer, initialState);


  const handleChange = (e) =>{
      const field =e.target.name
      const fieldValue= e.target.value
      const isConfirmPasswordTouched = state.touched.confirmPassword;
      const confirmEnteredPassword = state.fields.confirmPassword;
    dispatch({
        type:'UPDATE_FIELD',
        field:field,
        value:fieldValue
    })
    //  if password changes and confirm password is already touched revalidate it 
    if (field === 'password' && isConfirmPasswordTouched){
        const error = validateField(
            'confirmPassword',confirmEnteredPassword
        )
        dispatch({
            type: 'VALIDATE_FIELD',
            field:'confirmPassword',
            error:error

        })
    }
  }

  const validateField=(field,value)=>{
    switch (field){
        case 'email':
            // Check email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(value) ? null : 'Invalid email format';
        case 'password':
                  // Check password strength
            if (value.length < 8) return 'Password must be at least 8 characters';
            if (!/[A-Z]/.test(value)) return 'Must contain uppercase letter';
            if (!/[a-z]/.test(value)) return 'Must contain lowercase letter';
            if (!/\d/.test(value)) return 'Must contain a number';
            return null; // No errors
        
        case 'confirmPassword':
            return value === state.fields.password ? null : 'Passwords do not match';
        
        default:
            return null
    }
}



const handleSubmit =useCallback((e)=>{
    /*
    When a user clicks submit :
    1.mark all as touched (so incase the submit without filling anything, show all error messages not just the ones they have touched)
    2.have multiple dispatches for the three error states
    */
    e.preventDefault()
    const emailError = validateField('email',state.fields.email)
    const passwordError = validateField('password',state.fields.password)
    const confirmError =validateField('confirmPassword',state.fields.confirmPassword)

    // if any errors exist
    if (emailError || passwordError || confirmError){
        //mark all fields as touched (so errors show)
        dispatch({
            type:'SUBMIT_FORM',
            errors:{emailError,passwordError,confirmError}
        })       
    }
    console.log('Form submitted:',state.fields);
},[state.fields])


  const handleBlur = (e) =>{
    /*
    when the user leaves the field do :
     1.Mark the field as touched
     2.Validate it and set any error
    */
    const field = e.target.name
    const fieldValue = e.target.value;

    // mark as touched
    dispatch({
        type:'SET_TOUCHED',
        field:field
    })

    //validate
    const error= validateField(field,fieldValue)
    dispatch({
        type:'VALIDATE_FIELD',
        field:field,
        error:error
    })
  }
  
  const passwordStrength = useMemo(() =>{
    const pwd =state.fields.password
    if (!pwd ) return null

    let strength = 0
    if (pwd.length >= 8) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[a-z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;

    return strength

  },[state.fields.password])


  // TODO:
  // 1. Handle input onChange → dispatch UPDATE_FIELD
  // 2. Handle input onBlur → dispatch SET_TOUCHED, then validate
  // 3. Validation function: check email format, password strength, passwords match
  // 4. Submit handler: validate all, mark all touched if invalid
  // 5. useMemo for password strength (expensive regex)
  // 6. useCallback for handlers passed to memoized Button child
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="email"
        name="email"
        value={state.fields.email}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      {state.touched.email && state.errors.email && (
        <span className="error"> {state.errors.email}</span>
      )}

      <input 
      type="password" 
      name="password"
      value={state.fields.password}
      onChange={handleChange}
      onBlur={handleBlur}
      />
      {state.touched.password && state.errors.password  && (
        <span className="error"> {state.errors.password}</span>
      )}

      <input 
      type="password" 
      name="confirmPassword"
      value={state.fields.confirmPassword}
      onChange={handleChange}
      onBlur={handleBlur}
      />

      {state.touched.confirmPassword && state.errors.confirmPassword  && (
        <span className="error"> {state.errors.confirmPassword}</span>
      )}

    <button type="submit">SignUp</button>
    </form>

  );
}

