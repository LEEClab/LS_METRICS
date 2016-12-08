####################################################
#
# Ploting results of connectivity assessment
# LS Connectivity
#
# Bernardo Niebuhr - bernardo_brandaum at yahoo.com.br
# John Ribeiro - jw.ribeiro.rc at gmail.com
#
# No rights in the world are reserved
# Fell free to use, modify, and share
####################################################

# Loading libraries

# Working directory - where txt files are
setwd("C:\\Users\\LEEC B\\Desktop\\teste_ls_con")

# Loading data

prefix <- "lndscp_0001_Mapa0001_tif_bin"

# Patch size
patch <- read.table(paste(prefix, "_patch_AreaHA.txt", sep=""), header = T, sep = ",")

# Functional connectivity
nm <- list.files(pattern = "*clean_AreaHA.txt")

a <- strsplit(nm, split = "_*m_")
b <- c()
for(i in 1:length(nm)) b <- c(b, strsplit(a[[i]][1], split="_"))
ll <- length(b[[1]])
aa <- c()
for(i in 1:length(nm)) aa <- c(aa, as.numeric(b[[i]][ll]))
aa
bb <- sort(aa)
nm2 <- nm[order(aa)]

con <- list()
for(i in 1:length(nm2)) con[[i]] <- read.table(nm2[i], header = T, sep = ",")
names(con) <- bb
con

# Edges
nm <- list.files(pattern = "EDGE")
nm <- nm[grep("txt", nm)]

a <- strsplit(nm, split = "_*m_temp1.txt")
b <- c()
for(i in 1:length(nm)) b <- c(b, strsplit(a[[i]][1], split="EDGE"))
aa <- c()
for(i in 1:length(nm)) aa <- c(aa, as.numeric(b[[i]][2]))
aa
bb <- sort(aa)
nm2 <- nm[order(aa)]

edge <- matrix(, nrow = length(nm), ncol = 3)
for(i in 1:length(nm2)) {
  edge[i,] <- read.table(nm2[i], header = T, sep = ",")[,2]
}
rownames(edge) <- bb
colnames(edge) <- c("matrix", "edge", "interior")
edge

# Ploting
pdf("LS_connectivity_plots.pdf")

# Patch area
brk <- c(0, 10, 50, 100, 150, 200, 500, 1000, 1500, 2000)
n_lev <- hist(patch$HA, breaks = brk, plot = F)$counts
freq_lev <- n_lev/sum(n_lev)

#op <- par(mar = c(7, 4.5, 4, 2) + 0.1, mfrow=c(2,1))
op <- par(mar = c(7, 4.5, 4, 2) + 0.1)
barplot(freq_lev*100, las = 1, ylab = "Percentage of patches", xlab = "", 
        col = "grey", cex.lab = 1.7, cex.main = 1.5, 
        axes = FALSE, ylim = c(0, 80))
axis(2)
axis(1, at = c(0.8, 2, 3.2, 4.4, 5.6, 6.8, 8, 9.2, 10.4), 
     labels = c("0-10", "10-50", "50-100", "100-150", "150-200", 
                "200-500", "500-1000", "1000-1500", ">1500"), las = 2)
mtext("Class of patch size (ha)", side = 1, line = 5.5, cex = 1.5)
par(op)

patch2 <- patch[order(patch$HA),]
patch2$cum.area <- cumsum(patch2$HA)
when.break <- sapply(brk[2:length(brk)], function(x) max(which(patch2$HA < x)))
#cum.area <- ifelse(freq_lev > 0, patch2$cum.area[when.break], 0)
cum.area <- patch2$cum.area[when.break]
cum.area.f <- cum.area[1]
for(i in 2:length(cum.area)) cum.area.f <- c(cum.area.f, cum.area[i]-cum.area[i-1])
cum.area.rel <- cum.area.f/sum(cum.area.f)

op <- par(mar = c(7, 4.5, 4, 2) + 0.1)
barplot(cum.area.f, las = 1, ylab = "Area (ha)", xlab = "", 
        col = "grey", cex.lab = 1.7, cex.main = 1.5, 
        axes = FALSE, ylim = c(0, 1800))
axis(2)
axis(1, at = c(0.8, 2, 3.2, 4.4, 5.6, 6.8, 8, 9.2, 10.4), 
     labels = c("0-10", "10-50", "50-100", "100-150", "150-200", 
                "200-500", "500-1000", "1000-1500", ">1500"), las = 2)
mtext("Class of patch size (ha)", side = 1, line = 5.5, cex = 1.5)
text(c(0.8, 2, 3.2, 4.4, 5.6, 6.8, 8, 9.2, 10.4)-0.1,
     cum.area.f + 50, paste(round(cum.area.rel, 2),"%A", sep = ""), cex = 0.7)
text(c(0.8, 2, 3.2, 4.4, 5.6, 6.8, 8, 9.2, 10.4)-0.1, 
     cum.area.f + 120, paste(round(freq_lev, 2),"%NP", sep = ""), cex = 0.7)
par(op)

# FRAG patches
# We must do it!

# Connectivity
con
avg.cluster <- sapply(con, colMeans)[2,]
max.cluster <- sapply(con, function(x) sapply(x, max))[2,]

plot(as.numeric(attr(avg.cluster, "names")), avg.cluster, pch=21, bg=1,
     xlab = "Functional distance (m)", ylab = "Expected cluster size (ha)")
lines(as.numeric(attr(avg.cluster, "names")), avg.cluster)

# para o maximo nao faz sentido fazer agora...
plot(as.numeric(attr(max.cluster, "names")), max.cluster, pch=21, bg=1,
     xlab = "Functional distance (m)", ylab = "Maximum cluster size (ha)")
lines(as.numeric(attr(max.cluster, "names")), max.cluster)

# Edges

edge <- as.data.frame(edge)
tot <- sum(edge[1,2:3])
edge$cum.area <- edge$edge/tot

dists <- as.numeric(rownames(edge))
plot(dists, edge$cum.area, type = "b", log = "",
     xlab = "Edge distance (m)", ylab = "Cumulative area (%)")

brk <- c(50, 100, 250, 500, 750, 1000)
when.break <- sapply(brk, function(x) max(which(dists < x)))
#cum.area <- ifelse(freq_lev > 0, patch2$cum.area[when.break], 0)
cum.area <- edge$cum.area[when.break]
cum.area.f <- cum.area[1]
for(i in 2:length(cum.area)) cum.area.f <- c(cum.area.f, cum.area[i]-cum.area[i-1])

op <- par(mar = c(7, 4.5, 4, 2) + 0.1)
barplot(cum.area.f*100, las = 1, ylab = "%", xlab = "", 
        col = "grey", cex.lab = 1.7, cex.main = 1.5, 
        axes = FALSE)
axis(2)
axis(1, at = c(0.8, 2, 3.2, 4.4, 5.6, 6.8), 
     labels = c("0-50", "50-100", "100-250", "250-500", "500-750", 
                "750-1000"), las = 2)
mtext("Edge distance (m)", side = 1, line = 5.5, cex = 1.5)
par(op)

dev.off()
