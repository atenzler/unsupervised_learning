import torch as th

def process_data_for_model(cfg,
                           direction,
                           flux=None,
                           sunPos=None,
                           helPos=None,
                           xyalign=None,
                           targetID=None,
                           flux_sum2one=True,
                           flux_max2one=False,
                           apply_low_pass_filter=False,
                           apply_bilinear_smoothing=False):
    if not (direction == 'totrain' or direction == 'toreal'):
        raise Exception('Transform must be in totrain or toreal direction')

    if th.is_tensor(flux):
        flux = transform_flux(flux,
                              cfg,
                              direction,
                              sum2one=flux_sum2one,
                              max2one=flux_max2one,
                              lowpass=apply_low_pass_filter,
                              bilinear_smoothing=apply_bilinear_smoothing)

    if th.is_tensor(sunPos):
        sunPos = transform_sunPos(sunPos, cfg, direction)

    if th.is_tensor(helPos):
        helPos = transform_helPos(helPos, cfg, direction)

    if th.is_tensor(xyalign):
        xyalign = transform_xyalign(xyalign, cfg, direction)

    if th.is_tensor(targetID):
        targetID = transform_targetID(targetID, cfg, direction)

    return flux, sunPos, helPos, xyalign, targetID


def normalize_between(x, min_alt, max_alt, min_neu, max_neu):
    y = (max_neu - min_neu) * th.div((x - min_alt), max_alt - min_alt) + min_neu
    return y


def transform_sunPos(sunPos, cfg, direction):
    if not (direction == 'totrain' or direction == 'toreal'):
        raise Exception('Transform must be in totrain or toreal direction')

    # we are using ENU for the sunpos
    if sunPos.size(-1) == 3:
        if direction == 'totrain':
            sunPos[:, :, 0] = normalize_between(sunPos[:, :, 0],
                                                min_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[0],
                                                max_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[1],
                                                min_neu=0,
                                                max_neu=1)

            sunPos[:, :, 1] = normalize_between(sunPos[:, :, 1],
                                                min_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[0],
                                                max_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[1],
                                                min_neu=0,
                                                max_neu=1)

            sunPos[:, :, 2] = normalize_between(sunPos[:, :, 2],
                                                min_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_U[0],
                                                max_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_U[1],
                                                min_neu=0,
                                                max_neu=1)

        if direction == 'toreal':
            sunPos[:, :, 0] = normalize_between(sunPos[:, :, 0],
                                                min_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[0],
                                                max_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[1],
                                                min_alt=0,
                                                max_alt=1)

            sunPos[:, :, 1] = normalize_between(sunPos[:, :, 1],
                                                min_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[0],
                                                max_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[1],
                                                min_alt=0,
                                                max_alt=1)

            sunPos[:, :, 2] = normalize_between(sunPos[:, :, 2],
                                                min_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_U[0],
                                                max_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_U[1],
                                                min_alt=0,
                                                max_alt=1)
    elif sunPos.size(-1) == 2:
        if direction == 'totrain':
            sunPos[:, :, 0] = normalize_between(sunPos[:, :, 0],
                                                min_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_ELE[0],
                                                max_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_ELE[1],
                                                min_neu=0,
                                                max_neu=1)

            sunPos[:, :, 1] = normalize_between(sunPos[:, :, 1],
                                                min_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_AZI[0],
                                                max_alt=cfg.TARGETIMAGES.SUNPOS_LIMITS_AZI[1],
                                                min_neu=0,
                                                max_neu=1)

        if direction == 'toreal':
            sunPos[:, :, 0] = normalize_between(sunPos[:, :, 0],
                                                min_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[0],
                                                max_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_E[1],
                                                min_alt=0,
                                                max_alt=1)

            sunPos[:, :, 1] = normalize_between(sunPos[:, :, 1],
                                                min_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[0],
                                                max_neu=cfg.TARGETIMAGES.SUNPOS_LIMITS_N[1],
                                                min_alt=0,
                                                max_alt=1)
    else:
        raise Exception("Only ENU and sperical sunpos supported!")
    return sunPos


def transform_flux(fluxes,
                   cfg,
                   direction,
                   sum2one=True,
                   max2one=False,
                   bilinear_smoothing=False,
                   ):
    assert not sum2one == max2one, "Either sum2one or max2one"

    if not (direction == 'totrain' or direction == 'toreal'):
        raise Exception('Transform must be in totrain or toreal direction')

    flux_multiplyier = cfg.TARGETIMAGES.FLUX_MULTIPLYIER
    dim_compr = cfg.TARGETIMAGES.LOW_PASS_DIM
    if direction == 'totrain':

        if bilinear_smoothing == True:
            b, c, h, w = fluxes.size()
            fluxes = fluxes.view(b * c, 1, h, w)
            scale_factor = 2
            fluxes = th.nn.functional.interpolate(fluxes, scale_factor=scale_factor, mode='bilinear',
                                                  align_corners=False)
            fluxes = th.nn.functional.interpolate(fluxes, size=(w), mode='bilinear')
            fluxes = fluxes.view(b, c, h, w)


        fluxes = fluxes.clamp(min=0)
        if sum2one:
            fluxes = fluxes / th.sum(fluxes, dim=(2, 3), keepdim=True)
            fluxes = flux_multiplyier * fluxes
        elif max2one:
            fluxes = th.div(fluxes, th.max(fluxes, dim=2, keepdim=True)[0].max(dim=3, keepdim=True)[0])
        else:
            raise Exception("There was an error with flux normalization!")

    if direction == 'toreal':
        fluxes = fluxes / flux_multiplyier

    return fluxes


def transform_helPos(helPos, cfg, direction):
    if not (direction == 'totrain' or direction == 'toreal'):
        raise Exception('Transform must be in totrain or toreal direction')

    cfg_field = cfg.AC.FIELD
    x_min = cfg_field.SIZE_X[0]
    x_max = cfg_field.SIZE_X[1]
    sizey = cfg_field.SIZE_Y[1]
    sizez = cfg_field.SIZE_Z[1]

    if direction == 'totrain':
        # helPos[:,:,0] = th.div(helPos[:,:,0], sizex)
        helPos[:, :, 0] = normalize_between(helPos[:, :, 0], x_min, x_max, 0, 1)
        helPos[:, :, 1] = th.div(helPos[:, :, 1], sizey)
        helPos[:, :, 2] = th.div(helPos[:, :, 2], sizez)

    if direction == 'toreal':
        # helPos[:,:,0] = th.mul(helPos[:,:,0], sizex)
        helPos[:, :, 0] = normalize_between(helPos[:, :, 0], 0, 1, x_min, x_max)
        helPos[:, :, 1] = th.mul(helPos[:, :, 1], sizey)
        helPos[:, :, 2] = th.mul(helPos[:, :, 2], sizez)

    return helPos


class Dataset():
    def __init__(self,
                 datadir,
                 datafolders,
                 subscript,
                 geometry_model,
                 cfg,
                 fluxes_subscript,
                 crop_and_centralize_target_images=False,
                 renorm_surface=False,
                 appl_low_passfilter=False,
                 appl_bilinear_smoothing=False,
                 flattening_flux=False,
                 flux_sum2one=True,
                 flux_max2one=False,
                 cluster=False,
                 rank=0,
                 world_size=1,
                 distribute=False,
                 shuffle=True,
                 device='cpu'):

        zcntrllist = []
        fluxlist = []
        sunPoslist = []
        helPoslist = []
        helIDlist = []
        helIDlist_augment = []
        targetIDlist = []

        nth_considered_datafolder = 0
        for i, datafolder in enumerate(datafolders):
            geometry_str = datafolder.split('=')[1]
            if len(geometry_str.split('_')) > 1:
                geometry_str = geometry_str.split('_')[0]

            if not geometry_str == geometry_model:
                continue

            nth_considered_datafolder += 1

            if cluster == True:
                if distribute == True:
                    ziel_rank = nth_considered_datafolder % world_size
                    if not ziel_rank == rank:
                        continue

            print(f"rank {rank}: {nth_considered_datafolder}th datafolder {datafolder} was loaded!")
            datafolderdir = os.path.join(datadir, datafolder)
            datapackages = os.listdir(datafolderdir)

            # if fluxes_subscript == None:
            #     flux_subscript_string = ""
            # else:
            #     flux_subscript_string = f"_{}"
            for datapackage in datapackages:
                zcntrldir = os.path.join(datadir, datafolder, datapackage, f'zcntrl_{subscript}.pt')
                zcntrllist.append(th.load(zcntrldir).float())
                fluxdir = os.path.join(datadir, datafolder, datapackage, f'fluxes_{fluxes_subscript}.pt')
                fluxlist.append(th.load(fluxdir).float())
                sunPosdir = os.path.join(datadir, datafolder, datapackage, f'sunPos_{subscript}.pt')
                sunPoslist.append(th.load(sunPosdir).float())
                helPosdir = os.path.join(datadir, datafolder, datapackage, f'helPos_{subscript}.pt')
                helPoslist.append(th.load(helPosdir).unsqueeze(1))
                helIDdir = os.path.join(datadir, datafolder, datapackage, f'helIDs_{subscript}.pt')
                helIDlist.append(th.load(helIDdir))
                targetIDdir = os.path.join(datadir, datafolder, datapackage, f'targetIDs_{subscript}.pt')
                targetIDlist.append(th.load(targetIDdir))

                if subscript == "train":
                    helIDdir = os.path.join(datadir, datafolder, datapackage, f'helIDs_augment_{subscript}.pt')
                    helIDlist_augment.append(th.load(helIDdir))

        self.fluxes = th.cat(fluxlist, dim=0).float()
        del fluxlist

        self.zcntrls = th.cat(zcntrllist, dim=0).float()
        del zcntrllist
        self.zcntrls = utilsDL.zero_mean(self.zcntrls)

        self.minimum = cfg.DEEPLARTS.TRAIN.SURFACE_MIN
        self.maximum = cfg.DEEPLARTS.TRAIN.SURFACE_MAX

        assert th.min(self.zcntrls) > self.minimum, "The normalization of the surface will make problems!"
        assert th.max(self.zcntrls) < self.maximum, "The normalization of the surface will make problems!"

        if renorm_surface:
            self.zcntrls = normalize_between(x=self.zcntrls,
                                             min_alt=self.minimum,
                                             max_alt=self.maximum,
                                             min_neu=0,
                                             max_neu=1)

            self.zcntrls = utils.facets_to_surface(self.zcntrls)

        self.sunPos = th.cat(sunPoslist, dim=0).float()
        del sunPoslist

        self.helPos = th.cat(helPoslist, dim=0).float()
        del helPoslist

        self.targetID = th.cat(targetIDlist, dim=0)
        del targetIDlist

        self.helID = th.cat(helIDlist, dim=0)  # .unsqueeze(1).repeat(1,8)

        del helIDlist


        (self.fluxes,
         self.sunPos,
         self.helPos,
         self.targetID) = process_data_for_model(cfg,
                                                 direction='totrain',
                                                 flux=self.fluxes,
                                                 sunPos=self.sunPos,
                                                 helPos=self.helPos,
                                                 targetID=self.targetID,
                                                 apply_bilinear_smoothing=appl_bilinear_smoothing,
                                                 apply_low_pass_filter=appl_low_passfilter,
                                                 flux_sum2one=flux_sum2one,
                                                 flux_max2one=flux_max2one)

        """ # make data tensors to equal length across all processes
               if cluster and distribute:
            local_size = th.tensor(self.fluxes.size(0), device=device)
            global_average = hvd.allreduce(local_size)

            self.fluxes = resize_first_dim(self.fluxes, global_average.cpu().item())
            self.zcntrls = resize_first_dim(self.zcntrls, global_average.cpu().item())
            self.sunPos = resize_first_dim(self.sunPos, global_average.cpu().item())
            self.helPos = resize_first_dim(self.helPos, global_average.cpu().item())
            self.targetID = resize_first_dim(self.targetID, global_average.cpu().item())
            self.helID = resize_first_dim(self.helID, global_average.cpu().item())"""



        assert self.zcntrls.size(0) == self.fluxes.size(0)
        assert self.zcntrls.size(0) == self.fluxes.size(0)
        assert self.zcntrls.size(0) == self.sunPos.size(0)
        assert self.zcntrls.size(0) == self.helPos.size(0)
        assert self.zcntrls.size(0) == self.targetID.size(0)
        assert self.zcntrls.size(0) == self.helID.size(0)


        if flattening_flux:
            B, C, W, H = self.fluxes.size()

            self.fluxes = self.fluxes[:, 0, :, :].unsqueeze(1)
            self.sunPos = self.sunPos[:, 0, :].unsqueeze(1)
            self.targetID = self.targetID[:, 0].unsqueeze(1)

        # manual shuffling of the data:
        if shuffle:
            self.ndata = self.zcntrls.size(0)
            # shuffle image data
            idc = th.randperm(self.ndata)
            self.fluxes = self.fluxes[idc, :, :, :]
            self.zcntrls = self.zcntrls[idc, :, :, :]
            self.sunPos = self.sunPos[idc, :, :]
            self.helPos = self.helPos[idc, :, :]
            self.targetID = self.targetID[idc, :]
            self.helID = self.helID[idc]

        self.outputsize = self.zcntrls.size()
        self.inputsize = cfg.DEEPLARTS.TRAIN.TARGET_IMAGE_SIZE
        self.nsunPos = self.sunPos.size(1)
        # self.l2 = th.nn.functional.mse_loss(self.zcntrls, th.zeros_like(self.zcntrls))

        self.subscript = subscript

        assert self.fluxes.size(0) == self.zcntrls.size(0)

    def __len__(self):
        return len(self.zcntrls)

    def __getitem__(self, idx):
        fluxes = self.fluxes[idx]
        zcntrls = self.zcntrls[idx]
        sunPos = self.sunPos[idx]
        helPos = self.helPos[idx]
        targetID = self.targetID[idx]
        helID = self.helID[idx]
        return fluxes, zcntrls, sunPos, helPos, targetID, helID
