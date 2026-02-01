import { createSignal, createResource, Show, For } from 'solid-js';
import { inventoryService } from '../services/inventory';
import { serverService } from '../services/servers';
import { bookService } from '../services/books';
import { useAuth } from '../stores/auth';
import type { Inventory, InventoryCreate, Server, ServerCreate, Book, BookCreate } from '../types';
import '../styles/tabs.css';

export default function InventoryPage() {
    const { isAdmin } = useAuth();
    const [activeTab, setActiveTab] = createSignal<'inventory' | 'servers' | 'books'>('inventory');

    // Inventory state
    const [inventory, { refetch: refetchInventory }] = createResource<Inventory[]>(inventoryService.getInventory);
    const [showInventoryModal, setShowInventoryModal] = createSignal(false);
    const [editingInventoryItem, setEditingInventoryItem] = createSignal<Inventory | null>(null);
    const [inventoryFormData, setInventoryFormData] = createSignal<InventoryCreate>({
        name: '',
        quantity: 1,
        status: 'available',
    });

    // Servers state
    const [servers, { refetch: refetchServers }] = createResource<Server[]>(serverService.getServers);
    const [showServerModal, setShowServerModal] = createSignal(false);
    const [editingServer, setEditingServer] = createSignal<Server | null>(null);
    const [serverFormData, setServerFormData] = createSignal<ServerCreate>({
        name: '',
        hostname: '',
        ip_address: '',
        status: 'active',
    });

    // Books state
    const [books, { refetch: refetchBooks }] = createResource<Book[]>(bookService.getBooks);
    const [showBookModal, setShowBookModal] = createSignal(false);
    const [editingBook, setEditingBook] = createSignal<Book | null>(null);
    const [bookFormData, setBookFormData] = createSignal<BookCreate>({
        title: '',
        author: '',
        quantity: 1,
        status: 'available',
    });

    // Inventory handlers
    const handleInventorySubmit = async (e: Event) => {
        e.preventDefault();
        try {
            if (editingInventoryItem()) {
                await inventoryService.updateItem(editingInventoryItem()!.id, inventoryFormData());
            } else {
                await inventoryService.createItem(inventoryFormData());
            }
            setShowInventoryModal(false);
            setEditingInventoryItem(null);
            refetchInventory();
            setInventoryFormData({ name: '', quantity: 1, status: 'available' });
        } catch (error) {
            console.error('Failed to save inventory item:', error);
        }
    };

    const handleInventoryEdit = (item: Inventory) => {
        setEditingInventoryItem(item);
        setInventoryFormData({
            name: item.name,
            description: item.description,
            quantity: item.quantity,
            location: item.location,
            status: item.status,
            notes: item.notes,
        });
        setShowInventoryModal(true);
    };

    const handleInventoryDelete = async (id: number) => {
        if (confirm('Delete this inventory item?')) {
            try {
                await inventoryService.deleteItem(id);
                refetchInventory();
            } catch (error) {
                console.error('Failed to delete item:', error);
            }
        }
    };

    // Server handlers
    const handleServerSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            if (editingServer()) {
                await serverService.updateServer(editingServer()!.id, serverFormData());
            } else {
                await serverService.createServer(serverFormData());
            }
            setShowServerModal(false);
            setEditingServer(null);
            refetchServers();
            setServerFormData({ name: '', hostname: '', ip_address: '', status: 'active' });
        } catch (error) {
            console.error('Failed to save server:', error);
        }
    };

    const handleServerEdit = (server: Server) => {
        setEditingServer(server);
        setServerFormData({
            name: server.name,
            hostname: server.hostname,
            ip_address: server.ip_address,
            description: server.description,
            specs: server.specs,
            status: server.status,
            notes: server.notes,
        });
        setShowServerModal(true);
    };

    const handleServerDelete = async (id: number) => {
        if (confirm('Delete this server?')) {
            try {
                await serverService.deleteServer(id);
                refetchServers();
            } catch (error) {
                console.error('Failed to delete server:', error);
            }
        }
    };

    // Book handlers
    const handleBookSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            if (editingBook()) {
                await bookService.updateBook(editingBook()!.id, bookFormData());
            } else {
                await bookService.createBook(bookFormData());
            }
            setShowBookModal(false);
            setEditingBook(null);
            refetchBooks();
            setBookFormData({ title: '', author: '', quantity: 1, status: 'available' });
        } catch (error) {
            console.error('Failed to save book:', error);
        }
    };

    const handleBookEdit = (book: Book) => {
        setEditingBook(book);
        setBookFormData({
            title: book.title,
            author: book.author,
            quantity: book.quantity,
            status: book.status,
            location: book.location,
            description: book.description,
        });
        setShowBookModal(true);
    };

    const handleBookDelete = async (id: number) => {
        if (confirm('Delete this book?')) {
            try {
                await bookService.deleteBook(id);
                refetchBooks();
            } catch (error) {
                console.error('Failed to delete book:', error);
            }
        }
    };

    const openAddModal = () => {
        if (activeTab() === 'inventory') setShowInventoryModal(true);
        else if (activeTab() === 'servers') setShowServerModal(true);
        else if (activeTab() === 'books') setShowBookModal(true);
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>Inventory & Resources</h1>
                <button
                    class="btn btn-primary"
                    onClick={openAddModal}
                >
                    Add {activeTab().charAt(0).toUpperCase() + activeTab().slice(1, activeTab().length === 5 ? -1 : undefined).replace('server', 'Server').replace('inventor', 'Item').replace('book', 'Book')}
                </button>
            </div>

            <div class="tabs">
                <button
                    class={activeTab() === 'inventory' ? 'tab active' : 'tab'}
                    onClick={() => { console.log('Clicked Inventory'); setActiveTab('inventory'); }}
                >
                    Inventory
                </button>
                <button
                    class={activeTab() === 'servers' ? 'tab active' : 'tab'}
                    onClick={() => { console.log('Clicked Servers'); setActiveTab('servers'); }}
                >
                    Servers
                </button>
                <button
                    class={activeTab() === 'books' ? 'tab active' : 'tab'}
                    onClick={() => { console.log('Clicked Books'); setActiveTab('books'); }}
                >
                    Books
                </button>
            </div>

            {/* Inventory Tab */}
            <Show when={activeTab() === 'inventory'}>
                <Show when={inventory.loading}>
                    <p>Loading inventory...</p>
                </Show>

                <Show when={inventory()}>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Quantity</th>
                                    <th>Location</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <For each={inventory()}>
                                    {(item) => (
                                        <tr>
                                            <td>
                                                <strong>{item.name}</strong>
                                                <Show when={item.description}>
                                                    <br /><small>{item.description}</small>
                                                </Show>
                                            </td>
                                            <td>{item.quantity}</td>
                                            <td>{item.location || '-'}</td>
                                            <td>
                                                <span class={`badge badge-${item.status}`}>{item.status}</span>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm" onClick={() => handleInventoryEdit(item)}>
                                                    Edit
                                                </button>
                                                <Show when={isAdmin()}>
                                                    <button class="btn btn-sm btn-danger" onClick={() => handleInventoryDelete(item.id)}>
                                                        Delete
                                                    </button>
                                                </Show>
                                            </td>
                                        </tr>
                                    )}
                                </For>
                            </tbody>
                        </table>
                    </div>
                </Show>
            </Show>

            {/* Servers Tab */}
            <Show when={activeTab() === 'servers'}>
                <Show when={servers.loading}>
                    <p>Loading servers...</p>
                </Show>

                <Show when={servers()}>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Hostname</th>
                                    <th>IP Address</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <For each={servers()}>
                                    {(server) => (
                                        <tr>
                                            <td>
                                                <strong>{server.name}</strong>
                                                <Show when={server.description}>
                                                    <br /><small>{server.description}</small>
                                                </Show>
                                            </td>
                                            <td>{server.hostname}</td>
                                            <td>{server.ip_address}</td>
                                            <td>
                                                <span class={`badge badge-${server.status}`}>{server.status}</span>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm" onClick={() => handleServerEdit(server)}>
                                                    Edit
                                                </button>
                                                <Show when={isAdmin()}>
                                                    <button class="btn btn-sm btn-danger" onClick={() => handleServerDelete(server.id)}>
                                                        Delete
                                                    </button>
                                                </Show>
                                            </td>
                                        </tr>
                                    )}
                                </For>
                            </tbody>
                        </table>
                    </div>
                </Show>
            </Show>

            {/* Books Tab */}
            <Show when={activeTab() === 'books'}>
                <Show when={books.loading}>
                    <p>Loading books...</p>
                </Show>

                <Show when={books()}>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Author</th>
                                    <th>Location</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <For each={books()}>
                                    {(book) => (
                                        <tr>
                                            <td>
                                                <strong>{book.title}</strong>
                                                <Show when={book.description}>
                                                    <br /><small>{book.description}</small>
                                                </Show>
                                            </td>
                                            <td>{book.author}</td>
                                            <td>{book.location || '-'}</td>
                                            <td>
                                                <span class={`badge badge-${book.status}`}>{book.status}</span>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm" onClick={() => handleBookEdit(book)}>
                                                    Edit
                                                </button>
                                                <Show when={isAdmin()}>
                                                    <button class="btn btn-sm btn-danger" onClick={() => handleBookDelete(book.id)}>
                                                        Delete
                                                    </button>
                                                </Show>
                                            </td>
                                        </tr>
                                    )}
                                </For>
                            </tbody>
                        </table>
                    </div>
                </Show>
            </Show>

            {/* Inventory Modal */}
            <Show when={showInventoryModal()}>
                <div class="modal-overlay" onClick={() => { setShowInventoryModal(false); setEditingInventoryItem(null); }}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingInventoryItem() ? 'Edit Item' : 'Add Item'}</h2>
                        <form onSubmit={handleInventorySubmit}>
                            <div class="form-group">
                                <label>Name</label>
                                <input
                                    type="text"
                                    value={inventoryFormData().name}
                                    onInput={(e) => setInventoryFormData({ ...inventoryFormData(), name: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea
                                    value={inventoryFormData().description || ''}
                                    onInput={(e) => setInventoryFormData({ ...inventoryFormData(), description: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Quantity</label>
                                <input
                                    type="number"
                                    value={inventoryFormData().quantity}
                                    onInput={(e) => setInventoryFormData({ ...inventoryFormData(), quantity: parseInt(e.currentTarget.value) })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Location</label>
                                <input
                                    type="text"
                                    value={inventoryFormData().location || ''}
                                    onInput={(e) => setInventoryFormData({ ...inventoryFormData(), location: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Status</label>
                                <select
                                    value={inventoryFormData().status}
                                    onChange={(e) => setInventoryFormData({ ...inventoryFormData(), status: e.currentTarget.value })}
                                >
                                    <option value="available">Available</option>
                                    <option value="in_use">In Use</option>
                                    <option value="maintenance">Maintenance</option>
                                    <option value="retired">Retired</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Notes</label>
                                <textarea
                                    value={inventoryFormData().notes || ''}
                                    onInput={(e) => setInventoryFormData({ ...inventoryFormData(), notes: e.currentTarget.value })}
                                />
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => { setShowInventoryModal(false); setEditingInventoryItem(null); }}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Save
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>

            {/* Server Modal */}
            <Show when={showServerModal()}>
                <div class="modal-overlay" onClick={() => { setShowServerModal(false); setEditingServer(null); }}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingServer() ? 'Edit Server' : 'Add Server'}</h2>
                        <form onSubmit={handleServerSubmit}>
                            <div class="form-group">
                                <label>Name</label>
                                <input
                                    type="text"
                                    value={serverFormData().name}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), name: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Hostname</label>
                                <input
                                    type="text"
                                    value={serverFormData().hostname}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), hostname: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>IP Address</label>
                                <input
                                    type="text"
                                    value={serverFormData().ip_address}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), ip_address: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea
                                    value={serverFormData().description || ''}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), description: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Specs</label>
                                <textarea
                                    value={serverFormData().specs || ''}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), specs: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Status</label>
                                <select
                                    value={serverFormData().status}
                                    onChange={(e) => setServerFormData({ ...serverFormData(), status: e.currentTarget.value })}
                                >
                                    <option value="active">Active</option>
                                    <option value="maintenance">Maintenance</option>
                                    <option value="offline">Offline</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Notes</label>
                                <textarea
                                    value={serverFormData().notes || ''}
                                    onInput={(e) => setServerFormData({ ...serverFormData(), notes: e.currentTarget.value })}
                                />
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => { setShowServerModal(false); setEditingServer(null); }}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Save
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>

            {/* Book Modal */}
            <Show when={showBookModal()}>
                <div class="modal-overlay" onClick={() => { setShowBookModal(false); setEditingBook(null); }}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingBook() ? 'Edit Book' : 'Add Book'}</h2>
                        <form onSubmit={handleBookSubmit}>
                            <div class="form-group">
                                <label>Title</label>
                                <input
                                    type="text"
                                    value={bookFormData().title}
                                    onInput={(e) => setBookFormData({ ...bookFormData(), title: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Author</label>
                                <input
                                    type="text"
                                    value={bookFormData().author}
                                    onInput={(e) => setBookFormData({ ...bookFormData(), author: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Quantity</label>
                                <input
                                    type="number"
                                    value={bookFormData().quantity}
                                    onInput={(e) => setBookFormData({ ...bookFormData(), quantity: parseInt(e.currentTarget.value) })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Location</label>
                                <input
                                    type="text"
                                    value={bookFormData().location || ''}
                                    onInput={(e) => setBookFormData({ ...bookFormData(), location: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Status</label>
                                <select
                                    value={bookFormData().status}
                                    onChange={(e) => setBookFormData({ ...bookFormData(), status: e.currentTarget.value })}
                                >
                                    <option value="available">Available</option>
                                    <option value="borrowed">Borrowed</option>
                                    <option value="lost">Lost</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea
                                    value={bookFormData().description || ''}
                                    onInput={(e) => setBookFormData({ ...bookFormData(), description: e.currentTarget.value })}
                                />
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => { setShowBookModal(false); setEditingBook(null); }}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Save
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
