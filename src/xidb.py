import subprocess, os, uuid, datetime

REPO = 'repo'

def git(commands):
	print("git called with {commands}".format(commands=commands))
	
	pr = subprocess.Popen(['git'] + commands,   
		cwd=REPO,
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE, 
		shell=False)
	return pr.communicate()
	
out, err = git(['status'])	
print(out)


ProfileTemplate = """
<xidoc schema="[agent schema hash]">
     <xid>{guid}</xid>
     <name>{name}</name>
     <pubkey>pubkey hash</pubkey>
</xidoc>     
"""

MetadataTemplate = """
<xidoc schema="[metadata schema hash]">
     <xid>{xid}</xid>
     <name>{name}</name>
     <timestamp>{timestamp}</timestamp>
     <publisher>{xid}</publisher>
     <authors>
          <author>{xid}</author>
     </authors>
     <content>
          <hash>{xid}</hash>
          <type>text/xml</type>
     </content>
     <access>public access contract</access>
     <revision>private revision contract</revision>
</xidoc>
"""

SignatureTemplate = """
<Signature Id="{publisherID}" xmlns="http://www.w3.org/2000/09/xmldsig#">
     <SignedInfo>
          <CanonicalizationMethod Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>
          <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#dsa-sha1"/>
          <Reference URI="http://www.xidb.org/XID/{xid}">
               <Transforms>
                    <Transform Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>
               </Transforms>
               <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
               <DigestValue>{xid}</DigestValue>
          </Reference>
     </SignedInfo>
     <SignatureValue>...</SignatureValue>
</Signature>
"""

PublicationTemplate = """
<xidoc schema="[publication schema hash]">
     <metadata>{metadata}</xid>
	 <signatures>
		<publisher>{publisher}</publisher>
		<notary>{notary}</notary>
	 <signatures>
</xidoc>
"""

def getXID(agentID, file):
	out, err = git(['hash-object', os.path.join(agentID, file)])
	return out.strip().decode('utf-8')

def createAgent(name):
	guid = str(uuid.uuid4())
	agentFolder = os.path.join(REPO, guid)
	os.mkdir(agentFolder)
	
	def createFile(name, content):
		path = os.path.join(agentFolder, name)
		file = open(path, 'w+')
		file.write(content)
		file.close()
		return getXID(guid, name)

	uid = createFile('profile.xml', ProfileTemplate.format(guid=guid, name=name))
	xid = createFile('metadata.xml', MetadataTemplate.format(xid=uid, name=name, timestamp=datetime.datetime.now().isoformat('T')))
	pubsig = createFile('pubsig.xml', SignatureTemplate.format(publisherID=uid, xid=xid))
	notarysig = createFile('notarysig.xml', SignatureTemplate.format(publisherID='systemID', xid=xid))
	pubid = createFile('pub.xml', PublicationTemplate.format(metadata=xid, publisher=pubsig, notary=notarysig))
	
	out, err = git(['add', guid])
	print(out, err)
	
	out, err = git(['commit', '-m', "agent {name} created with xid {guid}".format(name=name, guid=guid)])
	print('commit...', out, err)
	
	return pubid
	
pubid = createAgent('squid')
print(pubid)

