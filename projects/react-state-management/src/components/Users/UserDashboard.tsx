import React,{type FC, useCallback, useEffect, useMemo, useState } from "react";
import { useDebounce } from "./hooks/useDebounce";

/*
what: a component that displays and manages users

//states needed
1.users,loading,error
2.searchInput,debouncedSearch
3.editingId,editForm

//build order
1.fetch + display
2.search with debounce
3.delete functionality
4.inline edit
5.optimize with memo / momoization 
    -useMemo for filterd users
    -usecallback for handlers
    -react.memo for user rows
*/

interface User {
  id: number;
  name: string;
  username: string;
  email: string;
  address: {
    street: string;
    suite: string;
    city: string;
    zipcode: string;
    geo: {
      lat: string;
      lng: string;
    };
  };
  phone: string;
  website: string;
  company: {
    name: string;
    catchPhrase: string;
    bs: string;
  };
}

export function UserDashboard() {
  const [users, setUsers] = useState<User[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const debouncedSearch = useDebounce(searchInput, 300);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ name: "", email: "" });

  /**
   * fetch a list of users from the json placeholder api
   */

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true);

      try {
        const response = await fetch(
          "https://jsonplaceholder.typicode.com/users"
        );
        if (!response.ok) throw new Error("Failed to fetch");

        const data: User[] = await response.json();
        setUsers(data);
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Error loading users."
        );
      } finally {
        setLoading(false);
      }
    };
    loadUsers();
  }, []);

  const filteredUsers = useMemo(
    () =>
      users?.filter((user) =>
        user.name.toLowerCase().includes(debouncedSearch.toLowerCase())
      ) ?? [],
    [users, debouncedSearch]
  );

  const handleDelete = useCallback(
    (id: number) => {
      setUsers(users?.filter((u) => u.id !== id) ?? []);
    },
    [ users,setUsers]
  );

  const handleEdit = useCallback(
    (user: User) => {
      setEditingId(user.id);
      setEditForm({ name: user.name, email: user.email });
    },
    [setEditingId, setEditForm]
  );

  const handleSave = useCallback(() => {
    setUsers(
      users?.map((u) => (u.id === editingId ? { ...u, ...editForm } : u)) ?? []
    );
    setEditingId(null);
  }, [ setEditingId,users,editForm]);

  const handleFormChange = useCallback(( field:'name'|'email',value:string)=>{
    setEditForm(prev=>({...prev,[field]:value}))
  },[]
  )

  

  return (
    <div className="p-6">
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}

      <input
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        placeholder="Search by name"
        className="border p-2 mb-4 w-full"
      />

{filteredUsers.map(user => (
  <UserRow
    key={user.id}
    user={user}
    isEditing={editingId === user.id}
    editForm={editForm}
    onEdit={() => handleEdit(user)}
    onDelete={() => handleDelete(user.id)}
    onSave={handleSave}
    onCancel={() => setEditingId(null)}
    onFormChange={handleFormChange}
  />
))}
    </div>
  );
}


// Move outside component
const UserRow = React.memo<{
  user: User;
  isEditing: boolean;
  editForm: { name: string; email: string };
  onEdit: () => void;
  onDelete: () => void;
  onSave: () => void;
  onCancel: () => void;
  onFormChange: (field: 'name' | 'email', value: string) => void;
}>(({ user, isEditing, editForm, onEdit, onDelete, onSave, onCancel, onFormChange }) => (
  <div className="border p-4 mb-2">
    {isEditing ? (
      <>
        <input value={editForm.name} onChange={e => onFormChange('name', e.target.value)} />
        <input value={editForm.email} onChange={e => onFormChange('email', e.target.value)} />
        <button onClick={onSave}>Save</button>
        <button onClick={onCancel}>Cancel</button>
      </>
    ) : (
      <>
        <h3>{user.name}</h3>
        <p>{user.email}</p>
        <p>{user.company.name}</p>
        <button onClick={onEdit}>Edit</button>
        <button onClick={onDelete}>Delete</button>
      </>
    )}
  </div>
));
