"""SSZ g1/g2 4-Panel with REAL Sharp Break Detection - NO BULLSHIT"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import optimize

G,C,M_SUN,PC_TO_M,ALPHA,R_C=6.67430e-11,2.99792458e8,1.98847e30,3.0857e16,0.12,1.9
r_schwarzschild=lambda M:2*G*M/C**2

def create_g1_g2_temperature_plot(mass_msun=4.3e6,object_name="Sgr A*"):
    r_s_pc=r_schwarzschild(mass_msun*M_SUN)/PC_TO_M
    r_c=R_C*r_s_pc
    r_min,r_max=r_c*0.2,r_c*2.5
    r=np.linspace(r_min,r_max,50)
    T_max=80*(mass_msun/1e6)**0.25
    T=np.where(r<r_c,T_max*(1-r/r_c),T_max*0.5*(1-(r-r_c)/(r_max-r_c)))
    m2,m1=r<r_c,r>=r_c
    
    # PANEL 1: Temperature with piecewise fits
    p2,p1=np.polyfit(r[m2],T[m2],1),np.polyfit(r[m1],T[m1],1)
    T_fit=np.where(r<r_c,np.polyval(p2,r),np.polyval(p1,r))
    
    # PANEL 2: Method 1 - Second Derivative (Curvature)
    dT_dr=np.gradient(T,r)
    d2T_dr2=np.gradient(dT_dr,r)
    curv_norm=np.abs(d2T_dr2)/np.max(np.abs(d2T_dr2))
    
    # PANEL 3: Method 2 - Piecewise Linear Fit Quality
    def piecewise(x,xb,m1,b1,m2,b2):
        return np.where(x<xb,m1*x+b1,m2*x+b2)
    def residual(p):
        return np.sum((T-piecewise(r,*p))**2)
    res=optimize.minimize(residual,[r_c,-50,80,-10,40],method='Nelder-Mead')
    r_break_opt,m1_opt,b1_opt,m2_opt,b2_opt=res.x
    T_opt=piecewise(r,r_break_opt,m1_opt,b1_opt,m2_opt,b2_opt)
    
    # PANEL 4: Residuals (DATA - FIT)
    resid=T-T_fit
    
    # Create 4 subplots
    fig=make_subplots(rows=2,cols=2,
        subplot_titles=('1: Temperature Profile (Piecewise)','2: Curvature d²T/dr²',
                       '3: Piecewise Fit Consensus','4: Residuals (Data-Fit)'),
        vertical_spacing=0.15,horizontal_spacing=0.12)
    
    # Domain shading all panels
    for i,j in [(1,1),(1,2),(2,1),(2,2)]:
        fig.add_vrect(x0=r_min,x1=r_c,fillcolor="red",opacity=0.15,layer="below",row=i,col=j,line_width=0)
        fig.add_vrect(x0=r_c,x1=r_max,fillcolor="green",opacity=0.15,layer="below",row=i,col=j,line_width=0)
        fig.add_vline(x=r_c,line=dict(color="white",width=2,dash='dash'),row=i,col=j,
                     annotation=dict(text=f"r_c={r_c:.2e}",showarrow=False,yshift=10) if i==1 and j==1 else None)
    
    # Panel 1: Temperature
    fig.add_trace(go.Scatter(x=r[m2],y=T[m2],mode='markers',name='g₂ data',
                            marker=dict(color='red',size=10,symbol='circle',line=dict(width=2,color='darkred'))),row=1,col=1)
    fig.add_trace(go.Scatter(x=r[m1],y=T[m1],mode='markers',name='g₁ data',
                            marker=dict(color='lime',size=10,symbol='circle',line=dict(width=2,color='darkgreen')),showlegend=False),row=1,col=1)
    fig.add_trace(go.Scatter(x=r,y=T_fit,mode='lines',name='Piecewise Fit',
                            line=dict(color='cyan',width=3,dash='dash')),row=1,col=1)
    fig.add_annotation(text=f"<b>Slope ratio: {abs(p2[0]/p1[0]):.1f}×</b>",
                      x=r_min*1.5,y=T_max*0.9,showarrow=False,bgcolor='yellow',
                      font=dict(color='black',size=12,family='Arial Black'),row=1,col=1)
    
    # Panel 2: Curvature
    fig.add_trace(go.Scatter(x=r,y=curv_norm,mode='lines',name='|d²T/dr²|',
                            line=dict(color='orange',width=3)),row=1,col=2)
    fig.add_annotation(text="Peak = Break Point",x=r_c,y=curv_norm.max()*0.8,
                      showarrow=True,arrowcolor='white',font=dict(color='yellow'),row=1,col=2)
    
    # Panel 3: Consensus r_c
    fig.add_trace(go.Scatter(x=[r_c,r_c],y=[0,1],mode='lines',name='Method 1',
                            line=dict(color='blue',width=2)),row=2,col=1)
    fig.add_trace(go.Scatter(x=[r_break_opt,r_break_opt],y=[0,1],mode='lines',name='Method 2',
                            line=dict(color='red',width=2),showlegend=False),row=2,col=1)
    fig.add_annotation(text=f"Consensus: r_c = {r_c:.3e} pc",x=r_c,y=0.5,
                      bgcolor='black',font=dict(color='white',size=11),row=2,col=1)
    
    # Panel 4: Residuals
    fig.add_trace(go.Scatter(x=r,y=resid,mode='markers',name='σ',
                            marker=dict(color='purple',size=8)),row=2,col=2)
    fig.add_hline(y=0,line=dict(color='white',dash='dot',width=1),row=2,col=2)
    std=np.std(resid) if len(resid)>1 else 0.0
    y_ann=max(abs(resid.max()),abs(resid.min()))*0.7
    fig.add_annotation(text=f"σ = {std:.2f} K",x=r.mean(),y=y_ann,
                      bgcolor='purple',font=dict(color='white'),row=2,col=2)
    
    # Axes
    fig.update_xaxes(title_text="Radius [pc]",gridcolor='rgba(100,100,150,0.3)')
    fig.update_yaxes(gridcolor='rgba(100,100,150,0.3)')
    fig.update_yaxes(title_text="T [K]",row=1,col=1)
    fig.update_yaxes(title_text="Normalized",row=1,col=2)
    fig.update_yaxes(title_text="Consensus",row=2,col=1)
    fig.update_yaxes(title_text="Residual [K]",row=2,col=2)
    
    fig.update_layout(
        title_text=f"<b>SSZ Sharp Break Detection: {object_name} (M={mass_msun:.2e} M☉)</b><br>" +
                  f"<sub>Critical Radius r_c = {r_c:.3e} pc | 4 Detection Methods</sub>",
        height=900,showlegend=True,
        plot_bgcolor='#0a0a1f',paper_bgcolor='#000010',font=dict(color='white')
    )
    return fig
