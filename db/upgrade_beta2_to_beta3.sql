begin;

create index test_domain_index on test using btree ("domain");
create index test_ended_id_queued on test using btree (ended, id, queued);
create index test_id_index on test using btree (id);

create index result_id_index on result using btree (id);
create index result_sensitive_testid on result using btree (sensitive, test_id);



CREATE SEQUENCE plugin_result_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.plugin_result_id_seq OWNER TO postgres;

--
-- Name: plugin_result; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE plugin_result (
    id integer DEFAULT nextval('plugin_result_id_seq'::regclass) NOT NULL,
    test_id integer NOT NULL,
    plugin character varying(255) NOT NULL,
    created timestamp without time zone DEFAULT now(),
    "domain" text,
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


ALTER TABLE public.plugin_result OWNER TO postgres;

create index plugin_result_plugin_domain_arg0_arg1_index on plugin_result using btree (plugin,"domain",arg0,arg1);


commit;
