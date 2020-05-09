from pylab import *
from scipy import *
import misc_utils, rwkos
import os
import pylab_util

t = arange(0, 1.0, 0.01)

def create_enc(tlist,start_low=True):
    if start_low:
        sig=zeros(shape(t))
    else:
        sig=ones(shape(t))
    curval=sig[0]
    for ct in tlist:
        ind=where(t>ct)[0]
        if ind.any():
            sig[ind]=1-curval
            curval=sig[ind[0]]
    return sig


def create_case(A_list, B_list, A_start=0, B_start=0):
    A = create_enc(A_list, start_low= not A_start)
    B = create_enc(B_list, start_low= not B_start)
    return A, B


def plot_case(A, B, fignum=1, asty='-', bcolor='r', bsty='--', clear=True, **kwargs):
    figure(fignum)
    if clear:
        clf()
    #plot(t, A, asty, t, B, bsty, **kwargs)
    step(t, A, **kwargs)#
    step(t, B, color=bcolor,linestyle=bsty, **kwargs)
    xlabel('Time (sec)')
    ylabel('Encoder Signals')
    ylim([-0.1, 1.1])


def save_case(filename, A, B):
    misc_utils.dump_vectors(filename, [t, A, B], \
                            labels=['Time (sec)','Enc. A','Enc. B'])


if __name__ == '__main__':
    #folder = rwkos.FindFullPath('mechatronics_2009/homework/encoders')
    #folder = rwkos.FindFullPath('/Users/rkrauss/siue/classes/458/Fall_2014/homework/encoders/')
    #folder = rwkos.FindFullPath('/Users/rkrauss/458_Fall_2015/prep/lecture_15_Encoders/')
    folder = rwkos.FindFullPath('/Users/rkrauss/458_Fall_2015/quizzes/quiz_04/')
    #folder = rwkos.FindFullPath('~/458_2012/final_exam/figs')
    outpat = 'encoders_case_%0.2d.txt'

    # case 1 lecture example
    A_list = [0.1, 0.3, 0.5, 0.7]
    B_list = [0.2, 0.4, 0.6, 0.8]
    case = 1


    # case 2 lecture example
    ## A_list = [0.3, 0.5, 0.7, 0.9]
    ## B_list = [0.2, 0.4, 0.6, 0.8]
    ## case = 2

    A, B = create_case(A_list, B_list, 0, 0)
    plot_case(A, B, fignum=case, bsty='--', linewidth=2.0)
    ylim([-0.1,1.45])
    legend(['A','B'],loc=1)
    curname = outpat % case
    fno, ext = os.path.splitext(curname)
    pdfname = fno + '.pdf'
    pdfpath = os.path.join(folder, pdfname)
    pngname = fno + '.png'
    pngpath = os.path.join(folder, pngname)
    outpath = os.path.join(folder, curname)
    yticks([0,1])
    tight_layout()
    save_case(outpath, A, B)
    pylab_util.mysave(pdfpath)
    savefig(pngpath)

##     # case 11
##     case = 11
##     A_list = [0.1, 0.3, 0.7, 0.9]
##     B_list = [0.2, 0.4, 0.6, 0.8]
##     A, B = create_case(A_list, B_list, 0, 0)
##     plot_case(A, B, case)
##     curname = outpat % case
##     outpath = os.path.join(folder, curname)
##     save_case(outpath, A, B)

##     # case 12
## case = 93
## A_list = [0.4, 0.6, 0.8, 0.9]
## B_list = [0.2, 0.3, 0.5, 0.7]
##     A, B = create_case(A_list, B_list, 1, 0)
##     plot_case(A, B, case)
##     curname = outpat % case
##     outpath = os.path.join(folder, curname)
##     save_case(outpath, A, B)

##     # case 13
##     case = 13
##     A_list = [0.1, 0.3, 0.7, 0.9]
##     B_list = [0.2, 0.4, 0.6]
##     A, B = create_case(A_list, B_list, 0, 1)
##     plot_case(A, B, fignum=case, bsty='--', linewidth=2.0)
##     ylim([-0.1,1.3])
##     legend(['A','B'])
##     curname = outpat % case
##     outpath = os.path.join(folder, curname)
##     #save_case(outpath, A, B)

    ## ## # case 14
    ## case = 14
    ## A_list = [0.1, 0.3, 0.5, 0.7, 0.8]
    ## B_list = [0.2, 0.4, 0.6, 0.9]
    ## A, B = create_case(A_list, B_list, 1, 0)

    ## plot_case(A, B, fignum=case, bsty='--', linewidth=2.0)
    ## ylim([-0.1,1.3])
    ## legend(['A','B'])
    ## curname = outpat % case
    ## fno, ext = os.path.splitext(curname)
    ## pdfname = fno + '.pdf'
    ## pdfpath = os.path.join(folder, pdfname)
    ## outpath = os.path.join(folder, curname)
    ## save_case(outpath, A, B)
    ## pylab_util.mysave(pdfpath)


    # case 15
    ## case = 17
    ## B_list = [0.1, 0.3, 0.5, 0.7]
    ## A_list = [0.4, 0.6, 0.8, 0.9]

    ## case = 18
    ## B_list = [0.1, 0.3, 0.5, 0.8]
    ## A_list = [0.2, 0.4, 0.6, 0.7]

    ## A, B = create_case(A_list, B_list, 0, 0)
    ## A_shift = A + 0.0075
    ## plot_case(A_shift, B, fignum=case, bsty='--', linewidth=2.0)
    ## grid(1)
    ## ylim([-0.1,1.3])
    ## legend(['A','B'])
    ## curname = outpat % case

    ## resave = 1

    ## if resave:
    ##     fno, ext = os.path.splitext(curname)
    ##     pdfname = fno + '.pdf'
    ##     pdfpath = os.path.join(folder, pdfname)
    ##     outpath = os.path.join(folder, curname)
    ##     save_case(outpath, A, B)
    ##     pylab_util.mysave(pdfpath)

    show()
