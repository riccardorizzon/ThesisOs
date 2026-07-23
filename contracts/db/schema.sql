CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chapters (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	parent_id UUID,
	order_index INTEGER NOT NULL,
	title TEXT NOT NULL,
	status VARCHAR(16) NOT NULL,
	content_md TEXT,
	summary TEXT,
	word_count INTEGER NOT NULL,
	version INTEGER NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(parent_id) REFERENCES chapters (id)
);

CREATE TABLE concepts (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) NOT NULL,
	slug VARCHAR(128) NOT NULL,
	title TEXT NOT NULL,
	subtitle TEXT,
	summary TEXT,
	definition TEXT,
	confidence VARCHAR(32) DEFAULT 'non_valutata' NOT NULL,
	knowledge_state VARCHAR(32) DEFAULT 'candidate' NOT NULL,
	is_core BOOLEAN DEFAULT false NOT NULL,
	created_by VARCHAR(32) DEFAULT 'operatore' NOT NULL,
	proposal_state VARCHAR(32) DEFAULT 'nessuna' NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_concepts_project_slug UNIQUE (project_id, slug)
);

CREATE TABLE conversations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	title TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE documents (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	title TEXT NOT NULL,
	author TEXT,
	source_type VARCHAR(16) NOT NULL,
	original_filename TEXT,
	gcs_uri TEXT,
	status VARCHAR(16) NOT NULL,
	page_count INTEGER,
	language VARCHAR(16),
	version INTEGER NOT NULL,
	parser VARCHAR(32),
	parsed_at TIMESTAMP WITH TIME ZONE,
	chunk_count INTEGER,
	error_message TEXT,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE embeddings (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	owner_type VARCHAR(16) NOT NULL,
	owner_id UUID NOT NULL,
	model VARCHAR(128) NOT NULL,
	dimension INTEGER NOT NULL,
	embedding VECTOR(768) NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	content_hash VARCHAR(64) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id, model)
);

CREATE TABLE events (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	type VARCHAR(64) NOT NULL,
	payload JSONB DEFAULT '{}'::jsonb NOT NULL,
	source VARCHAR(64),
	correlation_id VARCHAR(64),
	occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE memories (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	kind VARCHAR(16) NOT NULL,
	key TEXT,
	title TEXT,
	content TEXT NOT NULL,
	pinned BOOLEAN NOT NULL,
	source VARCHAR(16) NOT NULL,
	version INTEGER NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE projects (
	id VARCHAR(64) NOT NULL,
	display_name TEXT NOT NULL,
	kind VARCHAR(16) DEFAULT 'owned' NOT NULL,
	status VARCHAR(16) DEFAULT 'active' NOT NULL,
	settings JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE tasks (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	parent_task_id UUID,
	title TEXT NOT NULL,
	description TEXT,
	status VARCHAR(16) NOT NULL,
	owner_agent VARCHAR(64),
	priority INTEGER NOT NULL,
	payload JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(parent_task_id) REFERENCES tasks (id)
);

CREATE TABLE agent_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	conversation_id UUID,
	graph VARCHAR(64),
	trigger VARCHAR(64),
	input JSONB DEFAULT '{}'::jsonb NOT NULL,
	output JSONB,
	status VARCHAR(16) NOT NULL,
	error TEXT,
	started_at TIMESTAMP WITH TIME ZONE,
	finished_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);

CREATE TABLE chapter_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	chapter_id UUID NOT NULL,
	version INTEGER NOT NULL,
	change_kind VARCHAR(16) NOT NULL,
	title TEXT NOT NULL,
	status VARCHAR(16) NOT NULL,
	content_md TEXT,
	summary TEXT,
	word_count INTEGER NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	changed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_chapter_versions_chapter_id_version UNIQUE (chapter_id, version),
	FOREIGN KEY(chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
);

CREATE TABLE chunks (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	document_id UUID NOT NULL,
	chunk_index INTEGER NOT NULL,
	chunk_hash VARCHAR(64) NOT NULL,
	content TEXT NOT NULL,
	content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
	token_count INTEGER,
	page_from INTEGER,
	page_to INTEGER,
	section_path TEXT,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_chunks_document_id_chunk_index UNIQUE (document_id, chunk_index),
	CONSTRAINT uq_chunks_document_id_chunk_hash UNIQUE (document_id, chunk_hash),
	FOREIGN KEY(document_id) REFERENCES documents (id)
);

CREATE TABLE concept_relations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	from_concept_id UUID NOT NULL,
	to_concept_id UUID NOT NULL,
	relation_type VARCHAR(32) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_concept_relations_triple UNIQUE (from_concept_id, to_concept_id, relation_type),
	FOREIGN KEY(from_concept_id) REFERENCES concepts (id) ON DELETE CASCADE,
	FOREIGN KEY(to_concept_id) REFERENCES concepts (id) ON DELETE CASCADE
);

CREATE TABLE concept_source_links (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	concept_id UUID NOT NULL,
	source_slug VARCHAR(128) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_concept_source_links_pair UNIQUE (concept_id, source_slug),
	FOREIGN KEY(concept_id) REFERENCES concepts (id) ON DELETE CASCADE
);

CREATE TABLE document_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	document_id UUID NOT NULL,
	version INTEGER NOT NULL,
	title TEXT NOT NULL,
	author TEXT,
	source_type VARCHAR(16) NOT NULL,
	page_count INTEGER,
	chunk_count INTEGER,
	parser VARCHAR(32),
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	changed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	change_reason VARCHAR(16) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_document_versions_document_id_version UNIQUE (document_id, version),
	FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE CASCADE
);

CREATE TABLE memory_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	memory_id UUID NOT NULL,
	version INTEGER NOT NULL,
	title TEXT,
	content TEXT NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	source VARCHAR(16) NOT NULL,
	changed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(memory_id) REFERENCES memories (id) ON DELETE CASCADE
);

CREATE TABLE messages (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	conversation_id UUID NOT NULL,
	role VARCHAR(16) NOT NULL,
	content TEXT NOT NULL,
	tool_calls JSONB DEFAULT '[]'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);

CREATE TABLE notes (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) DEFAULT 'thesis-agent' NOT NULL,
	document_id UUID,
	chapter_id UUID,
	kind VARCHAR(16) NOT NULL,
	content TEXT NOT NULL,
	anchor JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(document_id) REFERENCES documents (id),
	FOREIGN KEY(chapter_id) REFERENCES chapters (id)
);

CREATE TABLE proposals (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	project_id VARCHAR(64) NOT NULL,
	chapter_id UUID NOT NULL,
	status VARCHAR(16) NOT NULL,
	original TEXT NOT NULL,
	proposed TEXT NOT NULL,
	action VARCHAR(32) NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(chapter_id) REFERENCES chapters (id)
);

CREATE TABLE sources (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	document_id UUID,
	type VARCHAR(32) NOT NULL,
	csl_json JSONB DEFAULT '{}'::jsonb NOT NULL,
	title TEXT,
	authors JSONB DEFAULT '[]'::jsonb NOT NULL,
	year INTEGER,
	doi TEXT,
	url TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE CASCADE
);

CREATE TABLE agent_steps (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	agent_run_id UUID NOT NULL,
	agent VARCHAR(64),
	phase VARCHAR(16),
	input JSONB DEFAULT '{}'::jsonb NOT NULL,
	output JSONB,
	status VARCHAR(16) NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	finished_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(agent_run_id) REFERENCES agent_runs (id)
);

CREATE TABLE citations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	source_id UUID NOT NULL,
	chapter_id UUID,
	locator TEXT,
	prefix TEXT,
	suffix TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(source_id) REFERENCES sources (id),
	FOREIGN KEY(chapter_id) REFERENCES chapters (id)
);
