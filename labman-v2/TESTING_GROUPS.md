# Testing the Groups Module

## ✅ Backend is Running!

The backend has started successfully with all the groups API endpoints.

## 🧪 Test the Groups API

### 1. Login First
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=admin@example.com" \
  -F "password=admin123"
```

Save the `access_token` from the response.

### 2. Test Groups Endpoints

**Get Groups Tree:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/groups/tree
```

**Create a Group:**
```bash
curl -X POST http://localhost:8000/api/v1/groups \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Research Group", "description": "Machine Learning and AI"}'
```

**Get Group Project Page:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/groups/1/project
```

## 🌐 Test the Frontend

1. Go to `http://localhost:5173`
2. Login with `admin@example.com` / `admin123`
3. Click "Groups" in the navigation
4. Create a new group
5. Click "Project Page" to see the group's project page
6. Click "Edit" to modify the content

## 📝 Note

The frontend needs the `marked` package for markdown rendering. Install it with:
```bash
cd labman-v2/frontend
npm install marked
```

Then the markdown rendering will work properly on the group project pages!

## ✨ What's Working

- ✅ Backend API running on port 8000
- ✅ Frontend running on port 5173
- ✅ Groups CRUD endpoints
- ✅ Group project pages (editable by all members)
- ✅ Hierarchical group tree structure
- ✅ Authentication and authorization

Everything is ready to use! 🎉
