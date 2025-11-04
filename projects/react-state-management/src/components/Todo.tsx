import { useReducer } from "react";

interface TodoState{
    todos:Todo[];
}
interface TodoAction{
    action:Actions[]
}

// const [state,dispatch] =useReducer(reducer,{
//     todos:[],
//     input:'',
//     count:0
// })

function todoReducer(state,action){
switch(action.type){
    case 'ADD_TODO':
        return {
            todos: [... state.todos, { id:Date.now(),text:action.text,completed:false} ],
            input:'',
            count:state.count+1
        }

        // 
    case 'TOGGLE_TODO':
        //
    case 'DELETE_TODO':
        //
    default:
        return state

}
}