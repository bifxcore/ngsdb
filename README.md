<h1>NGSdb: Comparative Genomics Database</h1>

<p>NGSdb is a relational database coupled with a Django web application (https://www.djangoproject.com/) that stores and allows users to view next-generation sequencing data. NGSdb currently has three
 components 1) sample module, which tracks the sample information (e.g., organism, growth phase) 2) Library module, which tracks the libraries constructed from samples (e.g., library type, sequencing 
 method, raw data files) 3) Analysis module, where the results from bioinformatics analyses are stored. Apart from storing and retrieving the data, the web interface serves as an analysis platform. </p>

<h2> Documentation </h2>

<h3> Requirements </h3>

NGSdb requires the following applications to run.

<ol>
    <li>Python (https://www.python.org/download/) </li>
    <li>Django (https://docs.djangoproject.com/en/dev/topics/install) </li>
    <li>Database System: Django supports PostgreSQL, MySQL, Oracle and SQLite.
</ol>

<h3>Install</h3>
Python, Django, and the Database System must be installed prior to NGSdb. See the above section on Requirements before proceeding.

<ol>
    <li>Create a new folder to store app.</li>
    <li>Clone the code into the new folder.
        <pre>
            <code>git clone https://github.com/bifxcore/ngsdb.git</code>
        </pre>
    </li>
    <li>Install Python's virutalenv package
        <pre>
            <code>pip install virtualenv</code>
        </pre>
    </li>
    <li>Create new virtualenv for NGSdb in separate folder.
        <pre>
            <code>virtualenv ngsdb</code>
        </pre>
    </li>
    <li>Activate virualenv.
        <pre>
            <code>source ngsdb/bin/activate</code>
        </pre>
    </li>
    <li>Install python requirements. The list of requirements is found within NGSdb/requirements/ folder.
        <pre>
            <code>pip install -r /path/to/ngsdb/requirements</code>
        </pre>
    </li>
</ol>