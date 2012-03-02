--
-- PostgreSQL database dump
--

SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bug_report; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE bug_report (
    id integer NOT NULL,
    email character varying(255),
    description text,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.bug_report OWNER TO postgres;

--
-- Name: bug_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE bug_report_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.bug_report_id_seq OWNER TO postgres;

--
-- Name: bug_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE bug_report_id_seq OWNED BY bug_report.id;


--
-- Name: frequency; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE frequency (
    id integer NOT NULL,
    "domain" character varying(255),
    max_tests integer DEFAULT 0,
    "interval" integer DEFAULT 0,
    description character varying(255),
    created_email character varying(255),
    created_ip character varying(50)
);


ALTER TABLE public.frequency OWNER TO postgres;

--
-- Name: COLUMN frequency."interval"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN frequency."interval" IS 'interval between tests in seconds';


--
-- Name: frequency_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE frequency_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.frequency_id_seq OWNER TO postgres;

--
-- Name: frequency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE frequency_id_seq OWNED BY frequency.id;


--
-- Name: frequency_ip; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE frequency_ip (
    id integer NOT NULL,
    ip character varying(50),
    max_tests integer,
    "interval" integer,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.frequency_ip OWNER TO postgres;

--
-- Name: frequency_ip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE frequency_ip_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.frequency_ip_id_seq OWNER TO postgres;

--
-- Name: frequency_ip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE frequency_ip_id_seq OWNED BY frequency_ip.id;


--
-- Name: live_feedback; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE live_feedback (
    id integer NOT NULL,
    test_id integer,
    created timestamp without time zone DEFAULT now(),
    message text,
    arg0 character varying(255),
    arg1 character varying(255),
    arg2 character varying(255),
    arg3 character varying(255),
    arg4 character varying(255),
    arg5 character varying(255),
    arg6 character varying(255),
    arg7 character varying(255),
    arg8 character varying(255),
    arg9 character varying(255)
);


ALTER TABLE public.live_feedback OWNER TO postgres;

--
-- Name: live_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE live_feedback_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.live_feedback_id_seq OWNER TO postgres;

--
-- Name: live_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE live_feedback_id_seq OWNED BY live_feedback.id;


--
-- Name: plugin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plugin (
    id integer NOT NULL,
    test_id integer,
    plugin character varying(100),
    started timestamp without time zone,
    status smallint DEFAULT 1,
    category character varying(50),
    ended timestamp without time zone
);


ALTER TABLE public.plugin OWNER TO postgres;

--
-- Name: plugin_config; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plugin_config (
    id integer NOT NULL,
    "key" character varying(255),
    value text,
    "comment" text
);


ALTER TABLE public.plugin_config OWNER TO postgres;

--
-- Name: plugin_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE plugin_config_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.plugin_config_id_seq OWNER TO postgres;

--
-- Name: plugin_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE plugin_config_id_seq OWNED BY plugin_config.id;


--
-- Name: plugin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE plugin_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.plugin_id_seq OWNER TO postgres;

--
-- Name: plugin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE plugin_id_seq OWNED BY plugin.id;


--
-- Name: plugin_result; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plugin_result (
    id integer NOT NULL,
    test_id integer,
    name character varying(100),
    value_text text,
    value_numeric numeric,
    table_id integer,
    child_table_id integer,
    plugin_id integer,
    extra character varying(20),
    created timestamp without time zone DEFAULT now(),
    plugin character varying(100)
);


ALTER TABLE public.plugin_result OWNER TO postgres;

--
-- Name: plugin_result_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE plugin_result_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.plugin_result_id_seq OWNER TO postgres;

--
-- Name: plugin_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE plugin_result_id_seq OWNED BY plugin_result.id;


--
-- Name: queue; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE queue (
    id integer NOT NULL,
    "domain" character varying(255),
    test_id integer,
    start_time timestamp without time zone DEFAULT now(),
    email character varying(255),
    ip character varying(50),
    extra text DEFAULT ''::text,
    waiting_input boolean DEFAULT false,
    slow boolean DEFAULT false,
    parent integer
);


ALTER TABLE public.queue OWNER TO postgres;

--
-- Name: queue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE queue_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.queue_id_seq OWNER TO postgres;

--
-- Name: queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE queue_id_seq OWNED BY queue.id;


--
-- Name: table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.table_id_seq OWNER TO postgres;

--
-- Name: test_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE test_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.test_id_seq OWNER TO postgres;

--
-- Name: test; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE test (
    id integer DEFAULT nextval('test_id_seq'::regclass) NOT NULL,
    "domain" character varying(255),
    email character varying(255),
    ip character varying(50),
    status smallint DEFAULT 1,
    queued timestamp without time zone,
    started timestamp without time zone,
    fast_finished timestamp without time zone,
    finished timestamp without time zone,
    slow boolean DEFAULT false,
    parent integer,
    sid character varying(32) DEFAULT md5(md5(((random())::text || (now())::text))),
    public smallint DEFAULT 1
);


ALTER TABLE public.test OWNER TO postgres;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE bug_report ALTER COLUMN id SET DEFAULT nextval('bug_report_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE frequency ALTER COLUMN id SET DEFAULT nextval('frequency_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE frequency_ip ALTER COLUMN id SET DEFAULT nextval('frequency_ip_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE live_feedback ALTER COLUMN id SET DEFAULT nextval('live_feedback_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE plugin ALTER COLUMN id SET DEFAULT nextval('plugin_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE plugin_config ALTER COLUMN id SET DEFAULT nextval('plugin_config_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE plugin_result ALTER COLUMN id SET DEFAULT nextval('plugin_result_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE queue ALTER COLUMN id SET DEFAULT nextval('queue_id_seq'::regclass);


--
-- Name: bug_report_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bug_report
    ADD CONSTRAINT bug_report_id PRIMARY KEY (id);


--
-- Name: frequency_ip_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY frequency_ip
    ADD CONSTRAINT frequency_ip_pkey PRIMARY KEY (id);


--
-- Name: frequency_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY frequency
    ADD CONSTRAINT frequency_pkey PRIMARY KEY (id);


--
-- Name: live_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY live_feedback
    ADD CONSTRAINT live_feedback_pkey PRIMARY KEY (id);


--
-- Name: plugin_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY plugin_config
    ADD CONSTRAINT plugin_config_pkey PRIMARY KEY (id);


--
-- Name: plugin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY plugin
    ADD CONSTRAINT plugin_pkey PRIMARY KEY (id);


--
-- Name: plugin_result_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY plugin_result
    ADD CONSTRAINT plugin_result_pkey PRIMARY KEY (id);


--
-- Name: queue_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY queue
    ADD CONSTRAINT queue_id_key PRIMARY KEY (id);


--
-- Name: test_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY test
    ADD CONSTRAINT test_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

