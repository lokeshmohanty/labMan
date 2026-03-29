export interface User {
    id: number;
    name: string;
    email: string;
    is_admin: boolean;
    email_notifications: boolean;
    created_at: string;
}

export interface Group {
    id: number;
    name: string;
    description?: string;
    parent_id?: number;
    lead_id?: number;
    lead_name?: string;
    created_at: string;
    has_project?: boolean;
}

export interface GroupTreeNode {
    id: number;
    name: string;
    description?: string;
    lead_id?: number;
    lead_name?: string;
    member_count: number;
    members: GroupTreeMember[];
    children: GroupTreeNode[];
    has_project?: boolean;
}

export interface GroupTreeMember {
    user_id: number;
    user_name: string;
    user_email: string;
}

export interface GroupCreate {
    name: string;
    description?: string;
    parent_id?: number;
    lead_id?: number;
}

export interface GroupUpdate {
    name?: string;
    description?: string;
    parent_id?: number;
    lead_id?: number;
}

export interface UserGroupCreate {
    user_id: number;
    role?: string;
}

export interface UserGroup {
    id: number;
    user_id: number;
    group_id: number;
    joined_at: string;
    user_name?: string;
    user_email?: string;
}

export interface GroupProject {
    group_id: number;
    problem_statement?: string;
    research_progress?: string;
    github_link?: string;
    manuscript_link?: string;
    start_date?: string;
    end_date?: string;
    comments?: string;
    updated_at: string;
    tasks: GroupTask[];
}

export interface GroupTask {
    id: number;
    project_id: number;
    title: string;
    description?: string;
    start_date?: string;
    end_date?: string;
    status: string;
    created_at: string;
}

export interface GroupTaskCreate {
    title: string;
    description?: string;
    start_date?: string;
    end_date?: string;
    status?: string;
}

// Meeting types
export interface Meeting {
    id: number;
    title: string;
    description?: string;
    meeting_time: string;
    group_id?: number;
    is_private: boolean;
    tags?: string;
    summary?: string;
    created_by: number;
    created_at: string;
    creator_name?: string;
    group_name?: string;
}

export interface MeetingCreate {
    title: string;
    description?: string;
    meeting_time: string;
    group_id?: number;
    is_private: boolean;
    tags?: string;
    summary?: string;
}

export interface MeetingResponse {
    response: string; // 'join' or 'wont_join'
}

// Content types
export interface Content {
    id: number;
    title: string;
    description?: string;
    filename: string;
    original_filename: string;
    file_size: number;
    mime_type?: string;
    uploaded_by: number;
    group_id?: number;
    research_plan_id?: number;
    created_at: string;
}

// Inventory types
export interface Inventory {
    id: number;
    name: string;
    description?: string;
    quantity: number;
    location?: string;
    status: string;
    notes?: string;
    created_at: string;
}

export interface InventoryCreate {
    name: string;
    description?: string;
    quantity: number;
    location?: string;
    status?: string;
    notes?: string;
}

// Server types
export interface Server {
    id: number;
    name: string;
    hostname?: string;
    ip_address?: string;
    description?: string;
    specs?: string;
    status: string;
    notes?: string;
    created_at: string;
}

export interface ServerCreate {
    name: string;
    hostname?: string;
    ip_address?: string;
    description?: string;
    specs?: string;
    status?: string;
    notes?: string;
}

// Research types
export interface ResearchPlan {
    user_id: number;
    problem_statement?: string;
    research_progress?: string;
    github_link?: string;
    manuscript_link?: string;
    start_date?: string;
    end_date?: string;
    comments?: string;
    updated_at: string;
    tasks: ResearchTask[];
}

export interface ResearchTask {
    id: number;
    plan_id: number;
    title: string;
    description?: string;
    start_date?: string;
    end_date?: string;
    status: string;
    previous_end_date?: string;
    created_at: string;
}

export interface ResearchTaskCreate {
    title: string;
    description?: string;
    start_date?: string;
    end_date?: string;
    status?: string;
}

// Books
export interface Book {
    id: number;
    title: string;
    author: string;
    quantity: number;
    status: string; // available, borrowed, lost
    location?: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface BookCreate {
    title: string;
    author: string;
    quantity: number;
    status: string;
    location?: string;
    description?: string;
}

export interface BookUpdate {
    title?: string;
    author?: string;
    quantity?: number;
    status?: string;
    location?: string;
    description?: string;
}
