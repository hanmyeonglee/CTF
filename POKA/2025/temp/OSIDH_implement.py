from sage.all import *
import pickle
import os

def get_abc(q):
	
	L=str(q).split(",")
	a=ZZ(L[0][4:])
	b=ZZ(L[1])
	c=ZZ(L[2][:-1])
	return (a,b,c)

def RandomFieldElt(a,p):

	return randint(0,p-1)+a*randint(0,p-1)

def RandomECElt(a,p,E):

	x=RandomFieldElt(a,p)
	A=E.a4()
	B=E.a6()
	y2=x**3+A*x+B
	while not y2.is_square():
		x=RandomFieldElt(a,p)
		y2=x**3+A*x+B
	y=y2.sqrt(extend=False,all=False)
	return E((x,y))

def Torsion_basis(a,p,E,q,N,v):

	m=N//q**v
	if v==2:
		P=m*RandomECElt(a,p,E)
		while P.is_zero():
			P=m*RandomECElt(a,p,E)

		Q=m*RandomECElt(a,p,E)
		while P.weil_pairing(Q,ZZ(q)).is_one():
			Q=m*RandomECElt(a,p,E)
	else:
		P=m*RandomECElt(a,p,E)
		while P.is_zero():
			P=m*RandomECElt(a,p,E)
		P1=q*P
		while not P1.is_zero():
			P=P1
			P1=q*P1

		Q=m*RandomECElt(a,p,E)
		Q1=q*Q
		while not Q1.is_zero():
			Q=Q1
			Q1=q*Q1
		while P.weil_pairing(Q,ZZ(q)).is_one():
			Q=m*RandomECElt(a,p,E)
			Q1=q*Q
			while not Q1.is_zero():
				Q=Q1
				Q1=q*Q1
	return (P,Q)

class OSIDH:
	def __init__(self,n,t,l,r,d_K=-4):
		
		if not ZZ(l).is_prime():
			raise ValueError("l should be a prime")
		if ZZ(d_K) not in [-3,-4]:
			raise ValueError("d_K should be -3 or -4")

		self.n=n
		self.t=t
		self.l=ZZ(l)
		self.r=r
		self.d_K=ZZ(d_K)

		L_q=[]
		q=2
		prod=l
		for j in range(t):
			while kronecker(d_K,q)==-1 or q==l:
				q=next_prime(q)
			L_q.append(q)
			prod*=q
			q=next_prime(q)
		self.L_q=L_q
		#print(L_q) [5, 13, 17, 29, 37, 41, 53, 61, 73, 89]
		self.L_mfq=[gp.qfbprimeform(d_K,q) for q in L_q]
		self.L_mfq_inv=[mfq**(-1) for mfq in self.L_mfq]

		threshold=l**(2*n)*L_q[-1]*-d_K
		while prod<threshold:
			prod*=l

		if d_K==-3:
			f=1
			if (f*prod)%3==2:
				f+=1
			if (f*prod)%3==1:
				p=f*prod+1
			else:
				p=f*prod-1
			while not p.is_prime():
				f+=1
				if (f*prod)%3==2:
					f+=1
				if (f*prod)%3==1:
					p=f*prod+1
				else:
					p=f*prod-1
		else:
			f=1
			if (f*prod)%4 in [1,3]:
				f+=1
			if (f*prod)%4==2:
				p=f*prod+1
			else:
				p=f*prod-1
			while not p.is_prime():
				f+=1
				if (f*prod)%4 in [1,3]:
					f+=1
				if (f*prod)%4==2:
					p=f*prod+1
				else:
					p=f*prod-1

		self.p=p

		self.N=(f*prod)**2
		L_v=[2]*(t+1)
		m=f*prod
		m=m//l
		while m%l==0:
			m=m//l
			L_v[0]+=2
		for i in range(t):
			m=m//L_q[i]
			while m%L_q[i]==0:
				m=m//L_q[i]
				L_v[i+1]+=2
		self.L_v=L_v



		self.F=GF(p**2,"a",proof="False")
		self.Fz=PolynomialRing(self.F,"z",sparse=True)

		self.L_phi=[]
		for q in [l]+L_q:
			try:
				filename=os.path.join("Modular_polynomials","phi_j_{0}.txt".format(str(q)))
				with open(filename,"r",encoding="utf-8") as file:
					L_P=[[0]*(q+2) for i in range(q+2)]
					for row in file:
						L_row=row.split(" ")
						L_ind=L_row[0][1:-1].split(",")
						u,v=int(L_ind[0]),int(L_ind[1])
						c=ZZ(L_row[1][0:-1])
						if u!=v:
							L_P[u][v]=c
							L_P[v][u]=c
						else:
							L_P[u][u]=c
					phi=[self.Fz(elt) for elt in L_P]
					self.L_phi.append(phi)
			except:
				raise ValueError("Prime q not in the database")

		# Origin curve
		a=self.F.gen()
		if d_K==-3:
			if p==f*prod-1:
				self.E0=EllipticCurve(self.F,[0,1])
			else:
				b=RandomFieldElt(a,p)
				while b.is_square():
					b=RandomFieldElt(a,p)
				self.E0=EllipticCurve(self.F,[0,b**3])
		else:
			if p==f*prod-1:
				self.E0=EllipticCurve(self.F,[1,0])
			else:
				b=RandomFieldElt(a,p)
				while b.is_square():
					b=RandomFieldElt(a,p)
				self.E0=EllipticCurve(self.F,[b**2,0])

		if d_K==-3:
			self.zeta=self.F.zeta(3)
		else:
			self.zeta=self.F(-1).sqrt(extend=False,all=False)


	def save(self,filename):
		with open(filename,"wb") as f:
			pickle.dump(self,f)
			
## Class of descending l-isogeny chains
class Chain:
	def __init__(self,osidh,L_j=[]):

		self.osidh=osidh
		if len(L_j)>0:
			self.L_j=L_j
		else:
			self.L_j=[]
			if osidh.d_K==-3:
				self.L_j.append(osidh.F(0))
			else:
				self.L_j.append(osidh.F(1728))

			phi_l=osidh.L_phi[0]
			Fz=osidh.Fz

			if osidh.n>=1:
				# Choice of the second j-invariant
				L_eval=[]
				for g in phi_l:
					L_eval.append(g(self.L_j[0]))
				f=Fz(L_eval)
				L_roots=f.roots(multiplicities=False)
				m=len(L_roots)
				i=randint(0,m-1)
				while L_roots[i]==self.L_j[0]:
					i=randint(0,m-1)
				self.L_j.append(L_roots[i])

				# Choice of the other j-invariants
				k=2
				while k<=osidh.n:
					L_eval=[]
					for g in phi_l:
						L_eval.append(g(self.L_j[k-1]))
					f=Fz(L_eval)
					L_roots=f.roots(multiplicities=False)
					m=len(L_roots)
					i=randint(0,m-1)
					while L_roots[i]==self.L_j[k-2]:
						i=randint(0,m-1)
					self.L_j.append(L_roots[i])
					k+=1

	def action_torsion(self,mfq,ind_q,i):
		
		p=self.osidh.p
		N=self.osidh.N
		L_v=self.osidh.L_v
		a=self.osidh.F.gen()

		L_E=[self.osidh.E0]
		l=self.osidh.l
		L_iso=[]
		L_iso_dual=[]
		for j in range(i):
			Pj,Qj=Torsion_basis(a,p,L_E[-1],l,N,L_v[0])
			phij=L_E[-1].isogeny(Pj)
			if phij.codomain().j_invariant()!=self.L_j[j+1]:
				T=Qj
				phij=L_E[-1].isogeny(T)
				k=0
				while phij.codomain().j_invariant()!=self.L_j[j+1] and k<=l-1:
					T+=Pj
					phij=L_E[-1].isogeny(T)
					k+=1
					
			Ej1=phij.codomain()
			Rj,Sj=phij(Pj),phij(Qj)
			if Rj.is_zero():
				phij_dual=Ej1.isogeny(Sj)
			else:
				phij_dual=Ej1.isogeny(Rj)
			# Make sure phij_dual is the domain of phij
			iso=phij_dual.codomain().isomorphism_to(L_E[-1])
			phij_dual.set_post_isomorphism(iso)

			L_iso.append(phij)
			L_iso_dual.append(phij_dual)
			L_E.append(Ej1)

		q,b,c=get_abc(mfq)
		if self.osidh.d_K==-3:
			lamb=(b-1)//2
		else:
			lamb=b//2

		P,Q=Torsion_basis(a,p,L_E[-1],q,N,L_v[ind_q+1])

		R,S=P,Q
		for j in range(i):
			R=L_iso_dual[i-1-j](R)
			S=L_iso_dual[i-1-j](S)

		zeta=self.osidh.zeta
		xR,yR=R.xy()
		xS,yS=S.xy()
		if self.osidh.d_K==-3:
			R1=L_E[0](zeta*xR,yR)
			S1=L_E[0](zeta*xS,yS)
		else:
			R1=L_E[0](-xR,zeta*yR)
			S1=L_E[0](-xS,zeta*yS)
		R=R1-lamb*R
		S=S1-lamb*S

		for j in range(i):
			R=L_iso[j](R)
			S=L_iso[j](S)

		if R.is_zero():
			T=P
		else:
			U=R
			k=1
			while U!=S:
				U+=R
				k+=1
			T=Q-k*P

		phi=L_E[-1].isogeny(T)
		return phi.codomain().j_invariant()

	def action_prime(self,mfq,ind_q):

		phi_l=self.osidh.L_phi[0]
		phi_q=self.osidh.L_phi[ind_q+1]
		Fz=self.osidh.Fz

		LF_j=[self.L_j[0]]
		for i in range(len(self.L_j)-1):
			L_eval=[]
			for g in phi_l:
				L_eval.append(g(LF_j[i]))
			f_l=Fz(L_eval)
			L_eval=[]
			for g in phi_q:
				L_eval.append(g(self.L_j[i+1]))
			f_q=Fz(L_eval)
			f=gcd(f_l,f_q)
			L_roots=f.roots(multiplicities=False)
			if len(L_roots)==1:
				LF_j.append(L_roots[0])
			elif len(L_roots)>=2:
				LF_j.append(self.action_torsion(mfq,ind_q,i+1))
			else:
				raise ValueError("Modular polynomials breakdown")

		return Chain(self.osidh,LF_j)

	def action(self,L_exp):

		out_chain=Chain(self.osidh,self.L_j.copy())
		L_mfq=self.osidh.L_mfq
		L_mfq_inv=self.osidh.L_mfq_inv

		for j in range(self.osidh.t):
			if L_exp[j]>=0:
				for k in range(L_exp[j]):
					out_chain=out_chain.action_prime(L_mfq[j],j)
			else:
				for k in range(-L_exp[j]):
					out_chain=out_chain.action_prime(L_mfq_inv[j],j)
		return out_chain
		
## Class of horizontal isogeny chains
class Chain_hor:
	def __init__(self,osidh,ind_q,j_center,L_plus,L_minus):

		self.osidh=osidh
		self.ind_q=ind_q
		self.j_center=j_center
		self.L_plus=L_plus
		self.L_minus=L_minus

	def action_step(self,ind_q,j,e):

		phi_q1=self.osidh.L_phi[self.ind_q+1] 
		phi_q2=self.osidh.L_phi[ind_q+1] 
		Fz=self.osidh.Fz

		L_plus=[j]
		L_minus=[j]

		if e>=0:
			k=1
			while k<=e:
				L_eval=[]
				for g in phi_q1:
					L_eval.append(g(L_plus[-1]))
				f_q1=Fz(L_eval)
				L_eval=[]
				for g in phi_q2:
					L_eval.append(g(self.L_plus[k-1]))
				f_q2=Fz(L_eval)
				f=gcd(f_q1,f_q2)
				L_roots=f.roots(multiplicities=False)
				L_plus.append(L_roots[0])
				k+=1
		else:
			k=1
			while k<=-e:
				L_eval=[]
				for g in phi_q1:
					L_eval.append(g(L_minus[-1]))
				f_q1=Fz(L_eval)
				L_eval=[]
				for g in phi_q2:
					L_eval.append(g(self.L_minus[k-1]))
				f_q2=Fz(L_eval)
				f=gcd(f_q1,f_q2)
				L_roots=f.roots(multiplicities=False)
				L_minus.append(L_roots[0])
				k+=1
		return Chain_hor(self.osidh,self.ind_q,j,L_plus[1::],L_minus[1::])
	
	def action_chain(self,chain,e,f):

		if e==0:
			if f>=0:
				return Chain_hor(chain.osidh,chain.ind_q,chain.j_center,chain.L_plus[0:f],[])
			else:
				return Chain_hor(chain.osidh,chain.ind_q,chain.j_center,[],chain.L_minus[0:-f])
		elif e>0:
			chain_out=chain
			for k in range(e):
				chain_out=chain_out.action_step(self.ind_q,self.L_plus[k],f)
		else:
			chain_out=chain
			for k in range(-e):
				chain_out=chain_out.action_step(self.ind_q,self.L_minus[k],f)
		return chain_out
	
def Action_hor_path(osidh,L_chains_hor,L_exp):

	t=osidh.t
	L_chains_path=[]

	if L_exp[0]>=0:
		L_chains_path.append(Chain_hor(osidh,0,L_chains_hor[0].j_center,L_chains_hor[0].L_plus[0:L_exp[0]],[]))
	else:
		L_chains_path.append(Chain_hor(osidh,0,L_chains_hor[0].j_center,[],L_chains_hor[0].L_minus[0:-L_exp[0]]))

	for j in range(1,t):
		chain=L_chains_hor[j]
		for k in range(j):
			chain=L_chains_path[k].action_chain(chain,L_exp[k],L_exp[j])
		L_chains_path.append(chain)
	return L_chains_path

def Action_hor(osidh,L_chains_hor,L_exp):

	t=osidh.t
	L_chains_path=Action_hor_path(osidh,L_chains_hor,L_exp)
	if L_exp[t-1]==0:
		return L_chains_path[t-1].j_center
	if L_exp[t-1]>0:
		return L_chains_path[t-1].L_plus[L_exp[t-1]-1]
	else:
		return L_chains_path[t-1].L_minus[-L_exp[t-1]-1]
